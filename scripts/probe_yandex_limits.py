# ruff: noqa: T201, INP001
"""Synthetic probe of Yandex Music edge rate limits.

Bypasses the provider's throttler and per-endpoint lock to measure RAW
Yandex behaviour. Intended to be run from inside the dev docker
container so the upstream ``yandex_music`` library is already on the
import path.

Each probe stops at the first 429 to avoid burning the strike ladder
needlessly. Between probes we pause for ``COOLDOWN_BETWEEN_PROBES_S`` so
Yandex's token-memory has time to lift.

Usage (from the host):

    docker compose -f docker-compose.dev.yml exec -e YA_TOKEN=<music_token> \
        ma /app/venv/bin/python /tmp/probe.py

Or:

    docker compose -f docker-compose.dev.yml cp scripts/probe_yandex_limits.py ma:/tmp/probe.py
    docker compose -f docker-compose.dev.yml exec ma /app/venv/bin/python /tmp/probe.py

The script reads ``YA_TOKEN`` from the environment. Get it from MA's
provider config or paste interactively.
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from collections.abc import Awaitable, Callable
from contextlib import suppress
from dataclasses import dataclass, field

from yandex_music import ClientAsync
from yandex_music.exceptions import NetworkError

# ---- Tunables --------------------------------------------------------------

COOLDOWN_BETWEEN_PROBES_S = 240  # 4 min — let Yandex's edge fully forget
MAX_ATTEMPTS_PER_PROBE = 12  # absolute upper bound so a probe always exits
SEARCH_QUERIES = (
    "queen",
    "beatles",
    "led zeppelin",
    "pink floyd",
    "metallica",
    "muse",
    "radiohead",
    "depeche mode",
    "kraftwerk",
    "abba",
    "u2",
    "oasis",
)


# ---- Helpers ---------------------------------------------------------------


def is_captcha_429(err: BaseException) -> bool:
    """Detect Yandex's smart-captcha 429 page in an exception."""
    if not isinstance(err, NetworkError):
        return False
    low = str(err).lower()
    return ("429" in low or "too many requests" in low or "rate limit" in low) and any(
        marker in low for marker in ("smart-captcha", "captcha_smart_qrcode", "about-429.html")
    )


@dataclass
class ProbeResult:
    """One measurement record."""

    name: str
    parameter: float | int
    success: bool
    elapsed_s: float
    note: str = ""
    history: list[str] = field(default_factory=list)


async def wait_for_clean_token(client: ClientAsync) -> bool:
    """Block until two consecutive ``search`` calls succeed without 429.

    Returns True if the token cooled within the deadline, False otherwise.
    """
    deadline = time.monotonic() + 600  # max 10 min
    last_print = 0.0
    while time.monotonic() < deadline:
        now = time.monotonic()
        if now - last_print > 30:
            remaining = int(deadline - now)
            print(f"  [wait_for_clean_token] probing… (deadline in {remaining}s)")
            last_print = now
        try:
            await client.search("probe-warmup", type_="track", page=0)
            await asyncio.sleep(2.0)
            await client.search("probe-warmup-2", type_="track", page=0)
            return True
        except Exception as err:
            if is_captcha_429(err):
                await asyncio.sleep(30)
                continue
            print(f"  [wait_for_clean_token] non-captcha error: {type(err).__name__}: {err}")
            return False
    return False


# ---- Probe 1: sustained RPS ------------------------------------------------


async def probe_sustained_rps(client: ClientAsync) -> ProbeResult:
    """Find the lowest inter-request interval Yandex tolerates for 10 calls."""
    print("\n=== Probe 1: sustained RPS (single endpoint) ===")
    intervals = (3.0, 2.0, 1.0, 0.5, 0.3, 0.2, 0.1)
    successful_rps = 0.0
    history: list[str] = []

    for interval in intervals:
        rps = 1.0 / interval
        print(f"\n  Trying {rps:.1f} RPS (interval={interval}s, 10 calls)")
        t0 = time.monotonic()
        tripped = False
        for i in range(10):
            try:
                await client.search(SEARCH_QUERIES[i % len(SEARCH_QUERIES)], type_="track", page=0)
            except Exception as err:
                tripped = True
                marker = "captcha" if is_captcha_429(err) else type(err).__name__
                history.append(f"  ✗ {rps:.1f} RPS tripped at call {i + 1}/10: {marker}")
                print(history[-1])
                break
            await asyncio.sleep(interval)

        if tripped:
            return ProbeResult(
                name="sustained_rps",
                parameter=successful_rps,
                success=successful_rps > 0,
                elapsed_s=time.monotonic() - t0,
                note=f"highest sustained = {successful_rps:.1f} RPS",
                history=history,
            )
        successful_rps = rps
        history.append(f"  ✓ {rps:.1f} RPS held for 10 calls ({time.monotonic() - t0:.1f}s)")
        print(history[-1])

    return ProbeResult(
        name="sustained_rps",
        parameter=successful_rps,
        success=True,
        elapsed_s=0.0,
        note=f"survived all tested rates up to {successful_rps:.1f} RPS",
        history=history,
    )


# ---- Probe 2: same-endpoint burst -------------------------------------------


async def probe_same_endpoint_burst(client: ClientAsync) -> ProbeResult:
    """Find the largest N parallel ``search`` calls that don't trigger 429."""
    print("\n=== Probe 2: same-endpoint parallel burst (search) ===")
    history: list[str] = []
    max_safe = 0
    for n in (2, 3, 4, 5, 6, 8, 10):
        print(f"\n  Firing {n} parallel search calls")
        tasks = [
            client.search(SEARCH_QUERIES[i % len(SEARCH_QUERIES)], type_="track", page=0)
            for i in range(n)
        ]
        t0 = time.monotonic()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.monotonic() - t0
        captcha_count = sum(
            1 for r in results if isinstance(r, BaseException) and is_captcha_429(r)
        )
        other_err_count = sum(
            1 for r in results if isinstance(r, BaseException) and not is_captcha_429(r)
        )
        if captcha_count == 0 and other_err_count == 0:
            max_safe = n
            history.append(f"  ✓ N={n} parallel: all OK in {elapsed:.2f}s")
            print(history[-1])
            await asyncio.sleep(5)
            continue
        history.append(
            f"  ✗ N={n} parallel: {captcha_count} captcha, "
            f"{other_err_count} other errors in {elapsed:.2f}s"
        )
        print(history[-1])
        return ProbeResult(
            name="same_endpoint_burst",
            parameter=max_safe,
            success=max_safe > 0,
            elapsed_s=elapsed,
            note=f"max safe parallel = {max_safe}; tripped at N={n}",
            history=history,
        )
    return ProbeResult(
        name="same_endpoint_burst",
        parameter=max_safe,
        success=True,
        elapsed_s=0.0,
        note=f"survived up to N={max_safe} parallel — no trip observed",
        history=history,
    )


# ---- Probe 3: cross-endpoint burst -----------------------------------------


async def probe_cross_endpoint_burst(client: ClientAsync) -> ProbeResult:
    """Repeat Probe 2 with each call hitting a different endpoint family."""
    print("\n=== Probe 3: cross-endpoint parallel burst ===")
    history: list[str] = []
    max_safe = 0

    def endpoint_callables() -> list[Callable[[], Awaitable[object]]]:
        # Lightweight read-only endpoints. Order kept stable so the same
        # combination is tested at each N.
        return [
            lambda: client.search("queen", type_="track", page=0),
            lambda: client.users_likes_artists(),
            lambda: client.users_likes_albums(),
            lambda: client.users_likes_tracks(),
            lambda: client.users_playlists_list(),
            lambda: client.feed(),
            lambda: client.landing(blocks=["chart"]),
            lambda: client.landing(blocks=["new-releases"]),
            lambda: client.landing(blocks=["new-playlists"]),
            lambda: client.tags("rock"),
        ]

    for n in (2, 3, 4, 5, 6, 8, 10):
        callables = endpoint_callables()[:n]
        print(f"\n  Firing {n} parallel calls to {n} different endpoints")
        t0 = time.monotonic()
        results = await asyncio.gather(*(c() for c in callables), return_exceptions=True)
        elapsed = time.monotonic() - t0
        captcha_count = sum(
            1 for r in results if isinstance(r, BaseException) and is_captcha_429(r)
        )
        other_err_count = sum(
            1 for r in results if isinstance(r, BaseException) and not is_captcha_429(r)
        )
        if captcha_count == 0 and other_err_count == 0:
            max_safe = n
            history.append(f"  ✓ N={n} cross-endpoint: all OK in {elapsed:.2f}s")
            print(history[-1])
            await asyncio.sleep(5)
            continue
        history.append(
            f"  ✗ N={n} cross-endpoint: {captcha_count} captcha, "
            f"{other_err_count} other errors in {elapsed:.2f}s"
        )
        print(history[-1])
        return ProbeResult(
            name="cross_endpoint_burst",
            parameter=max_safe,
            success=max_safe > 0,
            elapsed_s=elapsed,
            note=f"max safe parallel = {max_safe}; tripped at N={n}",
            history=history,
        )
    return ProbeResult(
        name="cross_endpoint_burst",
        parameter=max_safe,
        success=True,
        elapsed_s=0.0,
        note=f"survived up to N={max_safe} parallel — no trip observed",
        history=history,
    )


# ---- Probe 4: token memory --------------------------------------------------


async def probe_token_memory(client: ClientAsync) -> ProbeResult:
    """After a deliberate 429, find the minimum wait that lets us recover."""
    print("\n=== Probe 4: token memory (recovery time) ===")
    history: list[str] = []

    # Step 1: deliberately trigger a 429 with a 10-parallel burst.
    print("\n  Step 1: trip the token deliberately (10 parallel searches)")
    tasks = [
        client.search(SEARCH_QUERIES[i % len(SEARCH_QUERIES)], type_="track", page=0)
        for i in range(10)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    captcha_count = sum(1 for r in results if isinstance(r, BaseException) and is_captcha_429(r))
    if captcha_count == 0:
        return ProbeResult(
            name="token_memory",
            parameter=0,
            success=False,
            elapsed_s=0.0,
            note="could not trigger 429 with N=10 burst — Yandex tolerance higher than expected",
            history=["could not trigger initial 429"],
        )
    history.append(f"  ✓ tripped: {captcha_count}/10 returned captcha")
    print(history[-1])

    # Step 2: doubling-wait probe.
    waits = (15, 30, 60, 120, 240, 480)
    for wait in waits:
        print(f"\n  Step 2: waiting {wait}s, then 1 search…")
        await asyncio.sleep(wait)
        t0 = time.monotonic()
        try:
            await client.search("recovery-probe", type_="track", page=0)
            history.append(f"  ✓ recovered after {wait}s wait ({time.monotonic() - t0:.2f}s call)")
            print(history[-1])
            return ProbeResult(
                name="token_memory",
                parameter=wait,
                success=True,
                elapsed_s=time.monotonic() - t0,
                note=f"recovered after waiting {wait}s",
                history=history,
            )
        except Exception as err:
            marker = "captcha" if is_captcha_429(err) else type(err).__name__
            history.append(f"  ✗ still {marker} after {wait}s wait")
            print(history[-1])

    return ProbeResult(
        name="token_memory",
        parameter=waits[-1],
        success=False,
        elapsed_s=0.0,
        note=f"still tripped after {waits[-1]}s — Yandex memory ≥ longest probe interval",
        history=history,
    )


# ---- Orchestration ---------------------------------------------------------


async def main() -> int:
    """Run the four probes in sequence; return process exit code."""
    token = os.environ.get("YA_TOKEN", "").strip()
    if not token:
        print("ERROR: YA_TOKEN env var is required", file=sys.stderr)
        return 1

    print("Initialising raw yandex_music.ClientAsync (no provider throttler)…")
    client = ClientAsync(token)
    await client.init()

    results: list[ProbeResult] = []
    probes: list[tuple[str, Callable[[ClientAsync], Awaitable[ProbeResult]]]] = [
        ("sustained_rps", probe_sustained_rps),
        ("same_endpoint_burst", probe_same_endpoint_burst),
        ("cross_endpoint_burst", probe_cross_endpoint_burst),
        ("token_memory", probe_token_memory),
    ]

    for name, probe in probes:
        print(f"\n\n========== {name} ==========")
        print(f"Waiting up to 10 min for token to cool before {name}…")
        ok = await wait_for_clean_token(client)
        if not ok:
            print(f"  Token did not cool in time; skipping {name}.")
            continue
        try:
            result = await probe(client)
        except Exception as err:
            print(f"  Probe {name} crashed: {type(err).__name__}: {err}")
            continue
        results.append(result)
        print(f"\n  RESULT [{name}]: {result.note}")
        if name != probes[-1][0]:
            print(f"\n  Cooling down {COOLDOWN_BETWEEN_PROBES_S}s before next probe…")
            await asyncio.sleep(COOLDOWN_BETWEEN_PROBES_S)

    print("\n\n========== SUMMARY ==========")
    for r in results:
        print(f"  {r.name}: parameter={r.parameter} success={r.success} → {r.note}")
    return 0


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        sys.exit(asyncio.run(main()))
