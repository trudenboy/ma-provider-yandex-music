[← Back to README](../README.md)

# Development Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- ffmpeg 6.1+ (for MA integration tests)
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt-get install ffmpeg`
- Fork of [trudenboy/ma-server](https://github.com/trudenboy/ma-server) (for dev server)

## Setup

```bash
./scripts/setup.sh
```

Re-run after `git pull` — MA models version may change.

## Running Tests

```bash
# Unit tests (fast, no MA server needed)
pytest tests/ -m "not integration"

# Full test suite
pytest tests/

# With coverage
pytest --cov=provider --cov-report=html tests/
```

## Day-to-Day Workflow

### Branch naming

```
feature/<description>     # new functionality
fix/<description>         # bugfixes
chore/<description>       # maintenance, dependency updates
```

`<description>` — kebab-case, 2–4 words. Examples:
```
feature/my-wave-radio-support
fix/flac-seek-position-zero
chore/update-yandex-music-2.2.1
```

### Feature branch lifecycle

```bash
# 1. Create branch from dev
git checkout dev && git pull
git checkout -b feature/my-wave-radio-support

# 2. Development + tests
pytest tests/
pre-commit run --all-files

# 3. PR: feature/* → dev
git push origin feature/my-wave-radio-support
gh pr create --base dev --title "feat: add My Wave radio support"

# 4. CI passes → merge → delete branch
git push origin --delete feature/my-wave-radio-support
```

## Running Dev Server

Starts Music Assistant with live provider code (no Docker, isolated from other work):

```bash
./scripts/dev-server.sh
# UI: http://localhost:8095
```

Requires fork of ma-server. Discovery order:
1. `MA_SERVER_REPO=/path/to/ma-server ./scripts/dev-server.sh`
2. `echo "/path/to/ma-server" > ma-server.repo` (gitignored)
3. Autodetect: `../ma-server`, `~/Projects/ma-server`, `~/src/ma-server`, `~/dev/ma-server`

**Note**: Dev server binds port 8095 — don't run `pytest tests/` (with mass fixture) simultaneously.

## Code Quality

```bash
pre-commit run --all-files
```

Runs: ruff (lint + format), mypy (type check), codespell.

## Conventional Commits

Used for automatic CHANGELOG generation:
```
feat: add My Wave radio support
fix: fix FLAC seek at stream start
chore: update yandex-music library to 2.2.1
test: add streaming test for FLAC decrypt
```

## Release Process

1. PR: `dev` → `main`
2. Merge `main`
3. Trigger Release workflow: Actions → Release → Run workflow → enter version (e.g. `2.1.0`)
4. Workflow creates tag, GitHub Release (with auto-generated release notes)
5. Sync PR auto-created in [trudenboy/ma-server](https://github.com/trudenboy/ma-server)

## Working with Local MA Models

When developing alongside `music_assistant_models` changes:

```bash
uv pip install -e /path/to/music-assistant-models \
  --config-settings editable_mode=strict
# Restore after work:
uv pip install "music-assistant-models==<version>"
```

## Troubleshooting

**`sync-to-fork.yml` fails — FORK_SYNC_PAT expired**

Renew the PAT (needs `contents:write` on `trudenboy/ma-server`) then update the secret
in each provider repo via gh CLI:

```bash
gh secret set FORK_SYNC_PAT --body "$NEW_PAT" --repo trudenboy/ma-provider-yandex-music
gh secret set FORK_SYNC_PAT --body "$NEW_PAT" --repo trudenboy/ma-provider-kion-music
gh secret set FORK_SYNC_PAT --body "$NEW_PAT" --repo trudenboy/ma-provider-zvuk-music
gh secret set FORK_SYNC_PAT --body "$NEW_PAT" --repo trudenboy/ma-provider-msx-bridge
```

**Port 8095 already in use**

Another MA instance is running. Find and stop it:
```bash
lsof -i :8095
kill <PID>
```

Or use a different data dir to confirm it's a separate instance:
```bash
MA_DEV_DATA=~/.musicassistant-dev-alt ./scripts/dev-server.sh
# Note: port 8095 is still fixed — stop the other instance first
```

**`dev-server.sh` can't find the fork**

The script searches `../ma-server`, `~/Projects/ma-server`, `~/src/ma-server`, `~/dev/ma-server`.
If your fork is elsewhere, set `MA_SERVER_REPO` or create `ma-server.repo`:

```bash
# Option 1: env var
MA_SERVER_REPO=~/work/ma-server ./scripts/dev-server.sh

# Option 2: local override file (gitignored)
echo "~/work/ma-server" > ma-server.repo
./scripts/dev-server.sh
```

**Dev server running + need to run full pytest**

Port 8095 conflicts with the `mass` fixture used in integration tests.
Run only unit tests while dev-server is active:

```bash
pytest tests/ -m "not integration"
# or target specific test files:
pytest tests/test_parsers.py tests/test_api_client.py
```

Stop dev-server first for the full suite: `pytest tests/`

**`sync-to-fork.yml` ran but no PR created**

This is normal when the provider files haven't changed since the last sync.
`create-pull-request` skips PR creation if the diff is empty.

## E2E Checklist: Yandex Music

Run before upstream PR or major release:

### Setup
- [ ] Provider connects successfully (token accepted, no error on load)
- [ ] No errors in MA logs at startup

### Browse
- [ ] Browse → Yandex Music opens
- [ ] Liked Tracks displayed
- [ ] My Wave available
- [ ] Picks & Mixes shows playlists

### Search
- [ ] Track search returns results
- [ ] Artist search works
- [ ] Album search works

### Playback
- [ ] Track plays (AAC/MP3 quality)
- [ ] Track plays (FLAC quality, if premium)
- [ ] Seek works correctly
- [ ] No stall mid-track

### Library sync
- [ ] Liked Tracks sync to library
- [ ] Album art loads
