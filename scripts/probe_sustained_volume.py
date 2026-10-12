# ruff: noqa: T201, INP001, S311
"""
Synthetic probe of Yandex's sustained mixed-endpoint volume tolerance.

Complements ``probe_yandex_limits.py``. The original 4-probe suite
measured instant bursts and sequential RPS — both passed cleanly on
residential and datacenter — yet MA's own startup activity (continuous
mixed-endpoint traffic for ~30 seconds) still trips captcha. This
probe fills the gap: it sustains a fixed number of in-flight requests
across diverse endpoints for ``DURATION_S`` and records when (if at
all) Yandex trips.

Test matrix: concurrency cap = 1, 2, 3, 5. We sweep from low to high
to find the maximum sustained concurrency Yandex tolerates over the
duration window — which is what an MA installation actually maintains
between provider reload and end of initial sync.

Each test stops at the first 429 to keep the token's strike ladder
shallow. Between tests we pause ``COOLDOWN_BETWEEN_TESTS_S`` to let
Yandex's token memory lift.

Usage (from the host):

    docker compose -f docker-compose.dev.yml cp \
        scripts/probe_sustained_volume.py ma:/tmp/probe_sv.py
    docker compose -f docker-compose.dev.yml exec \
        -e YA_TOKEN=<music_token> \
        ma /app/venv/bin/python -u /tmp/probe_sv.py
"""

from __future__ import annotations

import asyncio
import os
import random
import sys
import time
from contextlib import suppress

from yandex_music import ClientAsync
from yandex_music.exceptions import NetworkError

# ---- Tunables --------------------------------------------------------------

DURATION_S = 30
CONCURRENCY_LEVELS = (1, 2, 3, 5)
COOLDOWN_BETWEEN_TESTS_S = 180  # 3 min
SPAWN_INTERVAL_S = 0.05  # how fast we try to fill the in-flight slots
SEARCH_QUERIES = (
    "queen",
    "beatles",
    "metallica",
    "pink floyd",
    "muse",
    "radiohead",
    "u2",
    "abba",
)


def is_captcha_429(err: BaseException) -> bool:
    """Detect Yandex's smart-captcha 429 page in an exception."""
    if not isinstance(err, NetworkError):
        return False
    low = str(err).lower()
    return ("429" in low or "too many requests" in low or "rate limit" in low) and any(
        m in low for m in ("smart-captcha", "captcha_smart_qrcode", "about-429.html")
    )


def make_call_factories(client: ClientAsync) -> list:
    """Return a list of zero-arg async callables, one per diverse endpoint family."""
    return [
        lambda: client.search(random.choice(SEARCH_QUERIES), type_="track", page=0),
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


async def wait_for_clean_token(client: ClientAsync, max_wait_s: int = 600) -> bool:
    """Block until two consecutive ``search`` calls succeed without 429."""
    deadline = time.monotonic() + max_wait_s
    last_print = 0.0
    while time.monotonic() < deadline:
        now = time.monotonic()
        if now - last_print > 30:
            print(
                f"  [wait_for_clean_token] probing… ({int(deadline - now)}s left)",
                flush=True,
            )
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
            print(
                f"  [wait_for_clean_token] non-captcha error: {type(err).__name__}: {err}",
                flush=True,
            )
            return False
    return False


async def sustained_volume_test(
    client: ClientAsync,
    *,
    concurrency: int,
    duration_s: int,
) -> dict:
    """
    Maintain ``concurrency`` in-flight requests for ``duration_s`` seconds.

    Returns a dict with ``total_completed``, ``tripped_at``, ``first_error``.
    """
    sem = asyncio.Semaphore(concurrency)
    factories = make_call_factories(client)
    start = time.monotonic()
    completed = 0
    tripped_at: float | None = None
    first_error: str | None = None
    completed_lock = asyncio.Lock()

    async def one_call(factory) -> None:
        nonlocal completed, tripped_at, first_error
        if tripped_at is not None:
            return
        async with sem:
            if tripped_at is not None:
                return
            try:
                await factory()
                async with completed_lock:
                    completed += 1
            except Exception as err:
                if is_captcha_429(err) and tripped_at is None:
                    tripped_at = time.monotonic() - start
                    first_error = "captcha"
                elif first_error is None:
                    first_error = f"{type(err).__name__}: {str(err)[:120]}"

    tasks: list[asyncio.Task] = []
    while time.monotonic() - start < duration_s and tripped_at is None:
        factory = random.choice(factories)
        tasks.append(asyncio.create_task(one_call(factory)))
        await asyncio.sleep(SPAWN_INTERVAL_S)

    await asyncio.gather(*tasks, return_exceptions=True)
    return {
        "concurrency": concurrency,
        "duration_s": duration_s,
        "completed": completed,
        "tripped_at": tripped_at,
        "first_error": first_error,
    }


async def main() -> int:
    """Run the sustained-volume sweep."""
    token = os.environ.get("YA_TOKEN", "").strip()
    if not token:
        print("ERROR: YA_TOKEN env var required", file=sys.stderr)
        return 1

    print(f"Initialising raw ClientAsync (DURATION_S={DURATION_S}s)…", flush=True)
    client = ClientAsync(token)
    await client.init()

    results: list[dict] = []
    for c in CONCURRENCY_LEVELS:
        print(f"\n========== concurrency={c} ==========", flush=True)
        print(f"Waiting for clean token before concurrency={c}…", flush=True)
        if not await wait_for_clean_token(client):
            print(f"  Token did not cool; skipping concurrency={c}", flush=True)
            continue

        print(f"\n[test c={c}] sustaining {c} in-flight for {DURATION_S}s…", flush=True)
        try:
            r = await sustained_volume_test(client, concurrency=c, duration_s=DURATION_S)
        except Exception as err:
            print(f"  Test crashed: {type(err).__name__}: {err}", flush=True)
            continue
        results.append(r)

        if r["tripped_at"] is None:
            print(
                f"  ✓ c={c}: clean for full {DURATION_S}s, {r['completed']} requests completed",
                flush=True,
            )
        else:
            print(
                f"  ✗ c={c}: tripped at {r['tripped_at']:.1f}s after {r['completed']} completed",
                flush=True,
            )

        if c != CONCURRENCY_LEVELS[-1]:
            print(
                f"\n  Cooling {COOLDOWN_BETWEEN_TESTS_S}s before next test…",
                flush=True,
            )
            await asyncio.sleep(COOLDOWN_BETWEEN_TESTS_S)

    print("\n\n========== SUMMARY ==========", flush=True)
    print(f"{'concurrency':<12} {'completed':<10} {'tripped_at':<12} verdict")
    for r in results:
        verdict = (
            "clean"
            if r["tripped_at"] is None
            else f"trip @ {r['tripped_at']:.1f}s ({r['first_error']})"
        )
        print(f"{r['concurrency']:<12} {r['completed']:<10} {verdict}")

    return 0


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        sys.exit(asyncio.run(main()))
