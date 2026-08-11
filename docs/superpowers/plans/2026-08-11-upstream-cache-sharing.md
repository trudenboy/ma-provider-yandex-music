# Upstream Playlist Cache Sharing Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace broken reverse-sync PRs #246, #248, and #252 with one tested provider change matching Music Assistant's final playlist request-sharing behavior after server PR #5464.

**Architecture:** Keep `get_playlist_tracks` as a routing method and put the standard Music Assistant cache decorator on each playlist-kind helper. Regular playlist loading moves intact into a dedicated helper; liked tracks, My Wave, and recommendations keep separate keys while identical concurrent calls share one in-flight request.

**Tech Stack:** Python 3.14, asyncio, Music Assistant `use_cache`, pytest, pytest-asyncio, Ruff, mypy, pre-commit, GitHub Actions.

## Global Constraints

- Do not modify `VERSION`; it is maintainer-owned.
- Do not introduce the removed `single_flight` decorator argument.
- Keep private methods at the bottom of `YandexMusicProvider`.
- Use Sphinx-style docstrings with `:param:` fields.
- Do not create a feature spec under `specs/inprogress/`; this is maintenance, not `feat:` work.
- Preserve unrelated user changes and the unrelated reverse-sync PR #249.
- Publish through a provider-repository PR targeting `dev`; never mutate `music-assistant/server` directly.

---

### Task 1: Prove request sharing and split playlist caching by kind

**Files:**
- Modify: `tests/conftest.py:1-90`
- Modify: `tests/test_recommendations.py:1-290`
- Modify: `tests/test_search_audiobooks.py:1-65`
- Modify: `tests/test_provider.py:1-305`
- Modify: `provider/provider.py:1411-1514`
- Modify: `provider/provider.py:3313-3445`

**Interfaces:**
- Consumes: `use_cache(expiration: int, allow_expired_cache: bool)`, `MY_WAVE_PLAYLIST_ID`, `LIKED_TRACKS_PLAYLIST_ID`, `MusicAssistant.cache`.
- Produces: `use_real_create_task(mass: MagicMock | MusicAssistant) -> None`; `_get_regular_playlist_tracks(self, prov_playlist_id: str, page: int) -> list[Track]`; cached `_get_my_wave_playlist_tracks(self, page: int) -> list[Track]`; cached `_get_liked_tracks_playlist_tracks(self, page: int) -> list[Track]`; uncached dispatcher `get_playlist_tracks(self, prov_playlist_id: str, page: int = 0) -> list[Track]`.

- [ ] **Step 1: Make cached-method test fixtures use real task creation**

Port upstream's `use_real_create_task` into `tests/conftest.py`. It binds
`MusicAssistant.create_task` to a mocked instance, supplies the running loop,
and keeps `create_task` as a `MagicMock` for existing assertions. Call it from
the `provider_mock` fixtures in `test_recommendations.py` and
`test_search_audiobooks.py`.

Add `_media_item_mock` to `test_recommendations.py`; its `__deepcopy__` returns
the same stand-in, matching value-like real media items. Use it for the parsed
track stand-ins in the My Wave success/duplicate tests and chart test.

- [ ] **Step 2: Re-run the previously failing baseline files**

```bash
uv run pytest tests/test_recommendations.py tests/test_search_audiobooks.py -q
```

Expected: both files pass against current upstream `dev`, eliminating the 43
baseline failures caused by mocked `mass.create_task`.

- [ ] **Step 3: Add concurrency-test imports and fixtures**

Add `asyncio`, `TYPE_CHECKING`, and `MY_WAVE_PLAYLIST_ID` imports. Under
`TYPE_CHECKING`, import `Callable`. Add `_StubConfig`, a `cached_provider`
fixture backed by an empty mocked cache plus `use_real_create_task`, and
`_wait_for_gated_fetch`, adapting the final upstream Yandex tests to this
standalone provider repository.

```python
class _StubConfig:
    instance_id = "yandex_music_test"

    def get_value(self, key: str, default: Any = None) -> Any:
        return default


@pytest.fixture
def cached_provider() -> tuple[YandexMusicProvider, mock.AsyncMock]:
    provider, mock_client = _make_provider()
    provider.mass = mock.MagicMock()
    provider.mass.cache = mock.AsyncMock()
    provider.mass.cache.get_with_freshness = mock.AsyncMock(
        return_value=(None, False, False)
    )
    provider.mass.cache.set = mock.AsyncMock()
    use_real_create_task(provider.mass)
    provider.config = _StubConfig()  # type: ignore[assignment]
    provider.manifest = mock.MagicMock(domain="yandex_music")
    provider._wave_states = {}
    return provider, mock_client


async def _wait_for_gated_fetch(started: Callable[[], bool]) -> None:
    for _ in range(200):
        if started():
            break
        await asyncio.sleep(0.01)
    else:
        pytest.fail("gated fetch never started")
    await asyncio.sleep(0.05)
```

- [ ] **Step 4: Add the two request-sharing characterization tests**

Add `test_regular_playlist_fetch_is_shared_between_callers` with a gated mocked `get_playlist`, and `test_my_wave_fetch_is_shared_between_callers` with a gated mocked `_fetch_rotor_session_batch`. Launch three identical calls with `asyncio.create_task`, release the gate, assert all results are empty lists, and assert the relevant backend await count is exactly one.

- [ ] **Step 5: Run the new characterization tests**

Run:

```bash
uv run pytest tests/test_provider.py::test_regular_playlist_fetch_is_shared_between_callers tests/test_provider.py::test_my_wave_fetch_is_shared_between_callers -q
```

Expected: both tests pass under the old top-level cache. They characterize the
request-sharing behavior that must remain green while cache ownership moves to
the helpers.

- [ ] **Step 6: Retarget the empty-batch regressions to the required helper**

Replace both uses of `YandexMusicProvider.get_playlist_tracks.__wrapped__` with `YandexMusicProvider._get_regular_playlist_tracks.__wrapped__`, passing page `0`. Run those two tests and confirm they fail with `AttributeError` because the helper does not exist yet.

```bash
uv run pytest tests/test_provider.py::test_get_playlist_tracks_continues_on_empty_batch tests/test_provider.py::test_get_playlist_tracks_raises_only_when_every_batch_is_empty -q
```

- [ ] **Step 7: Implement the final upstream cache topology**

Remove `@use_cache` from `get_playlist_tracks`. Keep only its logging and virtual-playlist routing, then return `await self._get_regular_playlist_tracks(prov_playlist_id, page)` for regular playlists.

Add `@use_cache(3600 * 3, allow_expired_cache=True)` to the My Wave and liked-track private helpers. Move the unchanged regular-playlist loading block into this private method after the virtual-playlist helpers:

```python
@use_cache(3600 * 3, allow_expired_cache=True)
async def _get_regular_playlist_tracks(
    self, prov_playlist_id: str, page: int
) -> list[Track]:
    """
    Get the tracks of a regular playlist.

    :param prov_playlist_id: The provider playlist ID.
    :param page: Page number for pagination.
    :return: List of Track objects.
    """
```

The new method body is exactly the current dispatcher block beginning with
`# Yandex Music API returns all playlist tracks in one call` and ending with
`return tracks`. It retains page termination, playlist-ID parsing, fallback
track hydration, batched detail loading, partial-batch warnings, the terminal
all-empty guard, and `InvalidDataError` handling without behavioral edits.

- [ ] **Step 8: Run focused tests until green**

```bash
uv run pytest tests/test_provider.py -q
```

Expected: all `tests/test_provider.py` tests pass, including the two concurrency tests and both empty-batch regressions.

- [ ] **Step 9: Run focused static checks**

```bash
uv run ruff check provider/provider.py tests/conftest.py tests/test_provider.py tests/test_recommendations.py tests/test_search_audiobooks.py
uv run ruff format --check provider/provider.py tests/conftest.py tests/test_provider.py tests/test_recommendations.py tests/test_search_audiobooks.py
uv run mypy provider/provider.py tests/conftest.py tests/test_provider.py tests/test_recommendations.py tests/test_search_audiobooks.py
```

Expected: all commands exit 0 without modifying files.

- [ ] **Step 10: Commit the behavior and tests**

```bash
git add provider/provider.py tests/conftest.py tests/test_provider.py tests/test_recommendations.py tests/test_search_audiobooks.py docs/superpowers
git commit -m "fix: align playlist request sharing with upstream"
```

---

### Task 2: Document the maintenance release and verify the repository

**Files:**
- Modify: `CHANGELOG.md:1-8`

**Interfaces:**
- Consumes: Keep a Changelog category ordering and the maintainer-owned `VERSION` policy.
- Produces: a `3.8.8` release-note block describing request sharing without internal paths, private symbols, or reverse-sync process wording.

- [ ] **Step 1: Add the changelog entry**

Insert above `3.8.6`:

```markdown
## [3.8.8] - 2026-08-11

### Changed

- Concurrent requests for the same regular, liked-tracks, or My Wave playlist now share one provider fetch, reducing duplicate Yandex requests during simultaneous playback starts.
```

- [ ] **Step 2: Verify no reverse-sync artifacts remain**

```bash
rg -n '<<<<<<<|=======|>>>>>>>|\.rej|Reverse-synced upstream PR #(5370|5430|5464)|WIP=1' provider tests specs CHANGELOG.md
```

Expected: no matches.

- [ ] **Step 3: Run the complete test suite**

```bash
uv run pytest -q
```

Expected: all tests pass.

- [ ] **Step 4: Run the repository gate**

```bash
uv run pre-commit run --all-files
```

Expected: every hook passes. If a formatting hook modifies files, inspect the changes and rerun until all hooks pass.

- [ ] **Step 5: Commit release documentation**

```bash
git add CHANGELOG.md
git commit -m "docs: record shared playlist requests"
```

---

### Task 3: Review, publish, and supersede broken reverse-sync PRs

**Files:**
- Review: complete branch diff against `dev`
- Publish: GitHub branch and draft PR metadata

**Interfaces:**
- Consumes: clean verified branch `fix/consolidate-upstream-cache-sharing`.
- Produces: one draft replacement PR targeting `dev`; closure comments on provider PRs #246, #248, and #252 linking the replacement.

- [ ] **Step 1: Perform final branch review**

```bash
git status -sb
git diff --check dev...HEAD
git diff --stat dev...HEAD
git diff dev...HEAD -- provider/provider.py tests/test_provider.py CHANGELOG.md docs/superpowers
```

Confirm the diff contains only the approved cache topology, tests, changelog, design, and implementation plan.

- [ ] **Step 2: Push the branch and create a draft PR**

Use title `fix: align Yandex playlist request sharing with upstream`. The body must summarize the consolidated upstream lineage (#5370, #5430, #5464), focused behavior, validation results, and state that it supersedes provider PRs #246, #248, and #252.

- [ ] **Step 3: Recheck GitHub checks and metadata**

Confirm the new PR is draft, targets `dev`, has no merge conflict, and has started or completed its expected checks. Do not mark it ready or merge it.

- [ ] **Step 4: Close superseded reverse-sync PRs**

Close provider PRs #246, #248, and #252 with a concise comment linking the replacement PR and explaining that their dependent upstream changes were consolidated into one tested net-port. Leave PR #249 unchanged.

- [ ] **Step 5: Report final evidence**

Return the replacement PR URL, local verification totals, current CI state, closed PR numbers, and any residual risk such as checks still running.
