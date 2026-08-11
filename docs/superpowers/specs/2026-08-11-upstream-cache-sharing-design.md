# Upstream Playlist Cache Sharing Consolidation

## Context

Upstream Music Assistant changed Yandex Music playlist caching across three
dependent pull requests: server PRs #5370, #5430, and #5464. Automated
reverse-sync created provider PRs #246, #248, and #252 independently. The
first two contain no functional provider patch, while #252 contains committed
conflict markers and assumes the method layout introduced by #5430.

Merging those generated PRs separately would either add no behavior or produce
invalid or double-cached code. The provider repository therefore needs one
manual net-port of the final upstream state.

## Considered Approaches

1. Resolve PR #252 in isolation. This is rejected because its patch assumes
   `_get_regular_playlist_tracks` already exists and would place a second cache
   decorator below the currently cached dispatcher.
2. Merge reverse-sync PRs #246, #248, and #252 in chronological order. This is
   rejected because #246 and #248 lost their functional patches during
   reverse-sync and contain only WIP documentation artifacts.
3. Apply the final upstream state directly in one provider PR. This is the
   selected approach because it preserves the upstream behavior, produces a
   reviewable diff, and supersedes all three broken generated PRs.

## Design

`get_playlist_tracks` becomes an uncached dispatcher. Caching moves to each
playlist-kind helper so regular, liked, and My Wave requests retain independent
cache keys while concurrent callers for the same request share one provider
fetch.

- `_get_my_wave_playlist_tracks(page)` receives the standard three-hour cache.
- `_get_liked_tracks_playlist_tracks(page)` receives the same cache.
- Regular-playlist loading moves unchanged into a new cached
  `_get_regular_playlist_tracks(prov_playlist_id, page)` helper.
- `_get_my_wave_recommendations` keeps its existing standard cache. No
  `single_flight` argument is introduced because current upstream removed that
  option and request sharing is now unconditional.

There are no dependency, setup-flow, authentication, model, or configuration
changes. `VERSION` remains maintainer-owned and is not modified.

## Tests

Existing empty-batch regression tests will call the unwrapped regular-playlist
helper after the dispatcher split. New concurrency tests will use an empty
mock cache with Music Assistant's real task-coalescing behavior and gated async
mocks to prove that three simultaneous calls produce one backend fetch for
both a regular playlist and My Wave.

The upstream single-flight cache helper now creates tracked tasks through
`MusicAssistant.create_task`. Provider unit-test fixtures that exercise cached
methods must therefore attach the real task-creation behavior to their mocked
Music Assistant instance. A provider-local test helper will mirror upstream's
`tests.common.use_real_create_task`, and cached-result media-item stand-ins will
preserve identity across `deepcopy`, matching real Music Assistant media items.
This is test-harness compatibility required by upstream #5370, not a production
behavior change.

Verification consists of the focused provider tests followed by the complete
repository test suite and `pre-commit run --all-files`.

## Release Documentation

Add a `3.8.8` changelog entry dated 2026-08-11 under the canonical `Changed`
heading. The entry describes the user-observable request-sharing behavior and
does not mention internal method names, file paths, review rounds, or reverse-
sync process details. No feature spec under `specs/inprogress/` is needed
because this is a maintenance alignment, not a `feat:` change.

## Delivery

Publish the implementation as a draft PR from
`fix/consolidate-upstream-cache-sharing` into `dev`. After the replacement PR
exists and its URL is known, close provider PRs #246, #248, and #252 as
superseded, linking each closure to the replacement PR. PR #249 is unrelated
and remains untouched.

## Acceptance Criteria

- The provider matches the final Yandex Music caching topology after upstream
  server PR #5464.
- Concurrent identical regular-playlist requests execute one backend fetch.
- Concurrent identical My Wave requests execute one rotor fetch.
- Empty-batch playlist behavior remains covered and unchanged.
- No conflict markers, `.rej` files, WIP specs, or process-noise changelog
  entries are introduced.
- Focused tests, the full test suite, and all pre-commit hooks pass.
- A draft replacement PR is open and broken reverse-sync PRs #246, #248, and
  #252 are closed with traceable supersession links.
