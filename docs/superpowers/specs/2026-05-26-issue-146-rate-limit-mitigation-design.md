# Design — Mitigate smart-captcha lockouts on initial sync (#146)

- **Date:** 2026-05-26
- **Driver issue:** [#146 — Yandex Music default cooldown active](https://github.com/trudenboy/ma-provider-yandex-music/issues/146)
- **Target branch:** `dev`
- **Conventional Commit type:** `fix(rate-limit):` (no `specs/` entry required per CLAUDE.md)
- **Version bump:** `3.5.4 → 3.5.5` (after review feedback is addressed)

## Problem

On a fresh install + auth, the initial library sync triggers Music Assistant's
metadata-refresh burst (multiple artist/album metadata calls in parallel).
With `THROTTLE_DEFAULT_RPS = 5`, the burst lands straight into Yandex's
smart-captcha edge layer. The first captcha response quarantines the entire
`default` throttler kind for `CAPTCHA_COOLDOWN_S = 600` seconds, which then
cascades into every other `default` call (playlists, search, recommendations)
failing with `Yandex Music default cooldown active` for 10 minutes.

The blast radius is the issue — a single captcha trip on one endpoint family
takes the whole provider offline for 10 minutes.

## Goals

1. Reduce the probability of the first captcha trip during initial sync.
2. Limit the blast radius when a captcha trip happens.
3. Make the first captcha trip cheaper to recover from (short cooldown,
   escalate only on repeats).
4. Keep all tuning knobs in `constants.py` so future telemetry-driven tuning
   does not require code changes.

## Non-goals

- Splitting `default` into many sub-buckets (`read`/`write`, `library`/`browse`).
  We add exactly one new kind — `metadata` — because the issue logs point
  squarely at the metadata-refresh burst, and a smaller change is easier to
  review and revert.
- Changing `RATE_LIMIT_COOLDOWN_S` (plain 429 path). Plain 429 already does
  not engage a kind-wide block; it only signals `backoff_time` on the failing
  request.
- Restructuring throttler internals beyond adding one kind.
- Modifying `file_info` or `rotor` kinds.

## Design

Four coordinated changes, all driven by constants in `provider/constants.py`.

### 1. New `metadata` throttler kind

`_get_throttler` gains a fourth bucket alongside `default`, `file_info`,
`rotor`. The following read-only calls are routed through `kind="metadata"`:

- `get_artist`
- `get_artist_info`
- `get_album`
- `get_artist_albums`
- `get_artist_tracks`

These are the calls Music Assistant invokes during the
"Update metadata for …" background tasks visible in the #146 log excerpt.

**Out of scope for `metadata`:** like/dislike actions, playlist edits, and
other write paths stay on `default` — MA does not burst them, so they are not
contributing to the captcha trigger.

### 2. Captcha cooldown escalation per kind

`_trigger_captcha_block` no longer always uses `CAPTCHA_COOLDOWN_S = 600`.
Instead, each kind maintains a `deque[float]` of recent captcha timestamps,
trimmed by `CAPTCHA_STRIKE_RETENTION_S` (default 1 hour). The cooldown is
selected from a tuple ladder:

```python
CAPTCHA_COOLDOWN_LADDER_S: Final[tuple[float, ...]] = (60.0, 300.0, 600.0)
```

- 1st strike in the retention window → 60s
- 2nd strike → 300s
- 3rd strike and beyond → 600s

Strike counter is per-kind, so a captcha on `metadata` does not escalate the
`default` counter and vice versa.

`RATE_LIMIT_COOLDOWN_S` (plain 429 path) is untouched — escalation applies
only to the captcha path.

### 3. Lower `THROTTLE_DEFAULT_RPS` and add `THROTTLE_METADATA_RPS`

- `THROTTLE_DEFAULT_RPS`: `5 → 3`
- `THROTTLE_METADATA_RPS`: new, `2`

Both are conservative defaults; the user explicitly chose "configurable via
constants" over hardcoded numbers, so future tuning is a one-line change.

### 4. Initial-sync jitter window

A jitter is applied to `default` and `metadata` calls **only** during the
first `INITIAL_SYNC_WINDOW_S` (default 60s) after `connect()` succeeds.
Inside the window, each call sleeps `random.uniform(0, INITIAL_SYNC_JITTER_S)`
(default 0.5s) before `throttler.acquire()`. After the window expires the
helper short-circuits to a no-op — no measurable overhead on steady-state
traffic.

`file_info` and `rotor` are excluded — `file_info` is on the streaming hot
path (latency matters), and `rotor` has its own throttler tuned separately.

## Constants summary

| Constant | Old | New |
|----------|-----|-----|
| `CAPTCHA_COOLDOWN_S` | `600.0` | **removed** (replaced by ladder) |
| `CAPTCHA_COOLDOWN_LADDER_S` | — | `(60.0, 300.0, 600.0)` |
| `CAPTCHA_STRIKE_RETENTION_S` | — | `3600.0` |
| `THROTTLE_DEFAULT_RPS` | `5` | `3` |
| `THROTTLE_METADATA_RPS` | — | `2` |
| `INITIAL_SYNC_JITTER_S` | — | `0.5` |
| `INITIAL_SYNC_WINDOW_S` | — | `60.0` |

## Touched files

| File | Change |
|------|--------|
| `provider/constants.py` | Replace `CAPTCHA_COOLDOWN_S` with `CAPTCHA_COOLDOWN_LADDER_S`; add `CAPTCHA_STRIKE_RETENTION_S`, `THROTTLE_METADATA_RPS`, `INITIAL_SYNC_JITTER_S`, `INITIAL_SYNC_WINDOW_S`; lower `THROTTLE_DEFAULT_RPS` to 3 |
| `provider/api_client.py` | `_get_throttler` (new `metadata` kind); `_trigger_captcha_block` (ladder + strike deque); `__init__` (`_captcha_strikes`, `_connected_at`); `connect` (set `_connected_at`); `_call_with_retry`/`_call_no_retry` (jitter helper); route metadata calls to `kind="metadata"` |
| `tests/test_api_client.py` | New tests for ladder, per-kind isolation, metadata routing, jitter window |
| `CHANGELOG.md` | New `## [3.5.5] - 2026-05-26` block under `### Fixed`, user-facing wording (no internal symbols / paths per CLAUDE.md changelog rules) |
| `VERSION` | `3.5.4 → 3.5.5` |

## Test plan (TDD)

Red → green → refactor, per CLAUDE.md. Each test is written first and
verified to fail before the implementation lands.

### Escalation ladder (Section 3.1)

- `test_captcha_first_strike_uses_short_cooldown` — 1st strike → `backoff_time == 60`.
- `test_captcha_second_strike_uses_medium_cooldown` — 2nd strike → `backoff_time == 300`.
- `test_captcha_third_strike_uses_max_cooldown` — 3rd+ strike → `backoff_time == 600`.
- `test_captcha_strikes_decay_after_retention_window` — after `> CAPTCHA_STRIKE_RETENTION_S`, ladder resets to 60s.
- `test_captcha_strikes_per_kind_isolated` — captcha on `metadata` does not bump `default` counter.

### Metadata kind (Section 3.2)

- `test_metadata_kind_uses_separate_throttler` — `_get_throttler("metadata") is not _get_throttler("default")`.
- `test_metadata_captcha_does_not_block_default` — captcha on `metadata` → next `default` call still passes `_check_block`.
- `test_<method>_uses_metadata_kind` (parametrized over `get_artist`, `get_artist_info`, `get_album`, `get_artist_albums`, `get_artist_tracks`).

### Initial-sync jitter (Section 3.3)

- `test_jitter_applied_within_initial_sync_window` — `asyncio.sleep` called with `0 < delay < INITIAL_SYNC_JITTER_S` for `default`/`metadata` inside the window.
- `test_jitter_skipped_after_initial_sync_window` — advance `time.monotonic` past window, no jitter sleep.
- `test_jitter_skipped_for_file_info_and_rotor` — jitter never applied for these kinds.

### Regression / pinning (Section 3.4)

- `test_throttle_default_rps_lowered` — pins `default` throttler RPS at `3` to catch accidental reverts.
- `test_existing_captcha_classification_unchanged` — `_classify_429` behaviour for smart-captcha markers, plain 429, non-429 errors stays untouched.

### Mocking philosophy

Per CLAUDE.md "test real behaviour, not mocks": mock only `time.monotonic`,
`asyncio.sleep`, and the upstream `NetworkError` raised by `yandex-music`.
Throttler is the real object — its real behaviour is part of what we are
verifying.

No `tests/__snapshots__/` changes — this is an internal rate-limit refactor
that does not touch parsers or streaming.

## Build sequence

Each step is a separate commit on `fix/issue-146-rate-limit-mitigation`
(branched from `dev`). Every commit passes `pre-commit run --all-files`
before the next step starts.

1. **Constants** — add `CAPTCHA_COOLDOWN_LADDER_S`, `CAPTCHA_STRIKE_RETENTION_S`,
   `THROTTLE_METADATA_RPS`, `INITIAL_SYNC_JITTER_S`, `INITIAL_SYNC_WINDOW_S`;
   lower `THROTTLE_DEFAULT_RPS` to 3; remove `CAPTCHA_COOLDOWN_S`.
   Commit: `refactor(constants): introduce rate-limit ladder + metadata throttler constants`.
2. **Ladder tests (RED)** — escalation tests fail. Commit: `test(rate-limit): cover captcha cooldown ladder + per-kind isolation`.
3. **Ladder impl (GREEN)** — `_captcha_strikes` deque + rewritten
   `_trigger_captcha_block` reading from the ladder; drop the now-unused
   `CAPTCHA_COOLDOWN_S` import in `api_client.py`. Tests pass.
   Commit: `fix(rate-limit): escalate captcha cooldown 60s → 300s → 600s per kind`.
4. **Metadata-kind tests (RED)** — tests fail. Commit: `test(rate-limit): cover new metadata throttler kind`.
5. **Metadata-kind impl (GREEN)** — `_get_throttler` branch; route the 5 metadata calls via `kind="metadata"`. Tests pass. Commit: `fix(rate-limit): route artist/album metadata calls to dedicated throttler kind`.
6. **Jitter tests (RED)** — tests fail. Commit: `test(rate-limit): cover initial-sync jitter window`.
7. **Jitter impl (GREEN)** — `_connected_at` + `_initial_sync_jitter` helper; integrate in `_call_with_retry`/`_call_no_retry`. Tests pass. Commit: `fix(rate-limit): jitter metadata + default calls during initial sync window`.
8. **Pinning tests** — `THROTTLE_DEFAULT_RPS` and classification regression tests. Commit: `test(rate-limit): pin lowered default RPS + existing classification behavior`.
9. **Bump + changelog** — `VERSION` → `3.5.5`, `CHANGELOG.md` entry, full `pre-commit run --all-files`, full `uv run pytest`, full `uv run mypy provider/`. Commit: `chore: bump VERSION to 3.5.5 + changelog`.
10. **PR** — `gh pr create` against `dev`. Title: `fix(rate-limit): mitigate smart-captcha lockouts on initial sync (#146)`. Body links #146, lists the four changes, includes test plan checklist. Do not self-merge — wait for maintainer review per CLAUDE.md "Ask before merging" rule.

## Rollback

Each step is an atomic commit. If a GREEN step fails to land within a
reasonable time, revert both the GREEN and its preceding RED commit rather
than relaxing the tests (per CLAUDE.md "Never modify existing tests to make
them pass").

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| New `metadata` kind misses a metadata call → captcha still hits `default` | Audit of `provider/provider.py` + `api_client.py` for direct `_client.get_artist*` / `get_album*` usage during Step 5; parametrized routing test covers all five known methods. |
| 60s first-strike cooldown too short → user retries immediately, second captcha hits, escalates straight to 300s | Acceptable: MA's retry cadence on metadata refresh is slower than 60s in practice; the ladder is intentionally conservative. If telemetry shows this happens, raise the first rung in `constants.py` — one-line change. |
| Jitter slows down legitimate steady-state traffic | Window-gated: after 60s post-connect, the helper is a no-op. No effect on long-running playback sessions. |
| Strike counter grows unbounded if `CAPTCHA_STRIKE_RETENTION_S` is hours and captchas are frequent | `deque` is trimmed on every `_trigger_captcha_block` call, so length is bounded by `len(CAPTCHA_COOLDOWN_LADDER_S) + epsilon`. |
| `random` is not seeded deterministically — flaky tests | Tests mock `asyncio.sleep` and assert on the delay range, not on a specific value. |

## Acceptance criteria

1. On a fresh install + auth, the first captcha trip during initial sync
   results in a 60-second user-visible backoff (not 600s).
2. A captcha trip on `metadata` does not block `default` calls (search,
   playlists, playback).
3. Repeated captcha trips within 1 hour escalate the cooldown:
   60s → 300s → 600s, per kind independently.
4. `THROTTLE_DEFAULT_RPS` is 3; `THROTTLE_METADATA_RPS` is 2; all jitter and
   ladder values live in `provider/constants.py`.
5. All existing tests in `tests/` remain green.
6. `pre-commit run --all-files` passes.
7. `CHANGELOG.md` entry uses only user-facing language (no internal
   identifiers, no `provider/*.py` paths) per CLAUDE.md changelog rules.
