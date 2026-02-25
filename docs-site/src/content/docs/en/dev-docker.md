---
title: Docker
---

# Yandex Music — Local Development with Docker

Run a full Music Assistant instance with the Yandex Music provider in a single command —
no Python, FFmpeg, or other dependencies required.

## Requirements

- [Docker](https://docs.docker.com/get-docker/)

## Quick Start

```bash
docker compose -f docker-compose.dev.yml up
```

Open **http://localhost:8095** in your browser.

## First Run: Creating a User

On the first start, MA launches a setup wizard:

1. **Create a user** — set a login and password (stored locally in `.ma-data/`)
2. Skip the Home Assistant integration if prompted
3. Login credentials persist between container restarts via the `.ma-data/` volume

## Connecting the Yandex Music Provider

After logging in:

1. Go to **Settings** → **Providers**
2. Find **Yandex Music** in the list — it is already available, the code is loaded automatically
3. Click **Add** and enter your credentials
4. Provider configuration is saved in `.ma-data/` and survives restarts

> 💡 If the provider does not appear — check the logs (`docker compose -f docker-compose.dev.yml logs`).
> Any startup error will be visible there.

## Container Management

| Action | Command |
|----------|---------|
| Start | `docker compose -f docker-compose.dev.yml up` |
| Start in background | `docker compose -f docker-compose.dev.yml up -d` |
| Stop | `docker compose -f docker-compose.dev.yml down` |
| Restart | `docker compose -f docker-compose.dev.yml restart` |
| Logs | `docker compose -f docker-compose.dev.yml logs -f` |
| Reset state | `rm -rf .ma-data/` → start again |

## Provider Code Changes

The code from `provider/` is mounted into the container via a symlink.
Changes are picked up after restarting the container — no image rebuild required:

```bash
docker compose -f docker-compose.dev.yml restart
```

## Persisting State

All MA configuration, provider credentials, and cache are stored in `.ma-data/` (add it to `.gitignore`).
The folder is created automatically on first run.
