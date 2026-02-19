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
4. Workflow creates CHANGELOG, tag, GitHub Release
5. Sync PR auto-created in [trudenboy/ma-server](https://github.com/trudenboy/ma-server)

## Working with Local MA Models

When developing alongside `music_assistant_models` changes:

```bash
uv pip install -e /path/to/music-assistant-models \
  --config-settings editable_mode=strict
# Restore after work:
uv pip install "music-assistant-models==<version>"
```
