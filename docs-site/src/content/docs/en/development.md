---
title: Development Environment
description: Setting up a development environment for the Yandex Music provider
---


## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- ffmpeg 6.1+ (for MA integration tests)
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt-get install ffmpeg`
- Fork of [trudenboy/ma-server](https://github.com/trudenboy/ma-server) (for the dev server)

## Setup

```bash
./scripts/setup.sh
```

Re-run after `git pull` — the MA models version may change.

## Running Tests

```bash
# Unit tests (no MA server required)
uv run pytest provider/tests/ -m "not integration"

# Full test suite
uv run pytest provider/tests/

# With coverage report
uv run pytest provider/tests/ --cov=provider/ --cov-report=html
```

## Branch Naming

```
feature/<description>    # new functionality
fix/<description>        # bug fixes
chore/<description>      # maintenance
```

`<description>` should be kebab-case, 2–4 words.

## Feature Branch Lifecycle

```bash
git checkout dev && git pull
git checkout -b feature/my-feature

# develop + test
uv run pytest provider/tests/
pre-commit run --all-files

# PR: feature/* → dev
git push origin feature/my-feature
gh pr create --base dev
```

## Running the Dev Server

```bash
./scripts/dev-server.sh
# UI: http://localhost:8095
```

## Conventional Commits

```
feat: add feature X
fix: fix bug Y
chore: update dependencies
test: add test for Z
```

## Release Process

1. PR: `dev` → `main`
2. Actions → Release → Run workflow → enter version
