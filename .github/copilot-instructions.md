# Copilot Instructions

This is a **Music Assistant (MA) provider plugin** for Yandex Music. It integrates with the MA server to stream music from Yandex Music and is loaded dynamically by MA at runtime.

## Commands

All commands use `uv run` (managed by [uv](https://docs.astral.sh/uv/)).

**Setup** (run after `git pull` too — MA models version may change):
```bash
./scripts/setup.sh
```

**Tests:**
```bash
# Unit tests only (fast, no MA server needed)
pytest tests/ -m "not integration"

# Full suite
pytest tests/

# Single test file or test
pytest tests/test_parsers.py
pytest tests/test_parsers.py::test_parse_track_with_version

# With coverage
pytest --cov=provider --cov-report=html tests/
```

**Lint / format / type-check:**
```bash
# All checks (recommended before PR)
uv run pre-commit run --all-files

# Individual tools
uv run ruff check provider/
uv run ruff format --check provider/
uv run mypy provider/
```

**Dev server** (live provider code, no Docker, port 8095):
```bash
./scripts/dev-server.sh
# UI: http://localhost:8095
```
> Do not run `pytest tests/` (full suite) while the dev server is running — port 8095 conflicts with the integration test `mass` fixture.

## Architecture

The provider is a single Python package in `provider/` that MA loads via `manifest.json`. The five source files each have a distinct responsibility:

| File | Role |
|---|---|
| `provider.py` | `YandexMusicProvider(MusicProvider)` — main MA plugin class; implements all MA provider API methods (browse, search, library, recommendations, playback hooks) |
| `api_client.py` | `YandexMusicClient` — thin async wrapper around `yandex-music`'s `ClientAsync`; handles auth, retries, and all Yandex API calls |
| `parsers.py` | Pure functions (`parse_track`, `parse_album`, `parse_artist`, `parse_playlist`) that convert Yandex API objects into MA model objects |
| `streaming.py` | `YandexMusicStreamingManager` — resolves stream URLs, selects quality, handles AES decryption of FLAC streams |
| `constants.py` | All string constants, IDs, quality labels, locale display-name dicts, tag/category mappings |

**Data flow:** `provider.py` → `api_client.py` (fetch raw Yandex objects) → `parsers.py` (convert to MA models) → returned to MA core. Streaming is a separate path: `provider.get_stream_details()` → `streaming.get_stream_details()` → `provider.get_audio_stream()` → `streaming.get_audio_stream()`.

**Import path in tests:** The provider is imported as `music_assistant.providers.yandex_music.*` (not via relative imports), matching how MA loads it at runtime.

## Key Conventions

### Item ID formats
- **Regular tracks:** plain `track_id` string
- **My Wave tracks:** composite `track_id@station_id` — the `@` separator (`RADIO_TRACK_ID_SEP`) encodes the rotor station for feedback; always split with `_parse_radio_item_id()` before API calls
- **Real playlists:** `owner_id:kind` (colon-separated, `PLAYLIST_ID_SPLITTER`)
- **Virtual playlists:** `my_wave` and `liked_tracks` (handled as special cases in `get_playlist` / `get_playlist_tracks`)

### Parser conventions
Parser functions in `parsers.py` follow the signature `parse_*(provider, yandex_object) -> MA model`. They receive a provider instance (for `get_item_mapping`, `instance_id`, `client.user_id`) but are otherwise pure — no async, no side effects.

### Test fixtures and snapshots
- JSON fixture files live in `tests/fixtures/{albums,artists,tracks,playlists}/` — these are real Yandex API response payloads
- Parser output is snapshot-tested via `syrupy`; snapshots live in `tests/__snapshots__/test_parsers.ambr`
- To update snapshots after an intentional parser change: `pytest tests/test_parsers.py --snapshot-update`
- `ProviderStub` in `tests/conftest.py` is a hand-written minimal stub (not `Mock`) used by parser tests

### Branch naming and commits
```
feature/<2-4-word-kebab>    # e.g. feature/my-wave-radio-support
fix/<2-4-word-kebab>        # e.g. fix/flac-seek-position-zero
chore/<2-4-word-kebab>      # e.g. chore/update-yandex-music-2.2.1
```

Commits follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `chore:`, `test:`, etc. PRs always target `dev` — never `main` directly.

### Caching
Use the `@use_cache` decorator from `music_assistant.controllers.cache` for expensive provider methods that return stable data. Check existing usages in `provider.py` before adding new cached calls.

### Locale-aware display names
`constants.py` has parallel `BROWSE_NAMES_RU` / `BROWSE_NAMES_EN` dicts. The provider picks the right one via `_get_browse_names()` based on the MA locale setting. Add new browse folder IDs to both dicts.
