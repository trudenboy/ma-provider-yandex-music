# Yandex Music Provider for Music Assistant

English | [Русский](README.md)

📖 <a href="https://trudenboy.github.io/ma-provider-yandex-music/">Documentation on GitHub Pages</a>

> Stream your [Yandex Music](https://music.yandex.ru/) library through [Music Assistant](https://music-assistant.io/) with full browse, search, radio, and lossless playback support.

## Quick Start (Docker)

```bash
# Clone the repo
git clone https://github.com/trudenboy/ma-provider-yandex-music.git
cd ma-provider-yandex-music

# Start Music Assistant with the provider pre-loaded
docker compose -f docker-compose.dev.yml up
```

Open the MA web UI at `http://localhost:8095`, then go to **Settings → Music Sources → Add Source → Yandex Music** and enter your OAuth token.

For the full Docker dev environment guide see [docs/dev-docker.md](docs/dev-docker.md).

## Features

- **Library sync** — Artists, Albums, Tracks (Liked), Playlists synced to MA library
- **Library editing** — Like / unlike Artists, Albums, Tracks directly from MA
- **Browse** — Liked Tracks, My Wave radio, Picks & Mixes (mood/era/activity/genre), Feed, Chart, Artists, Albums, Playlists
- **Recommendations** — personalised "For You" sections surfaced as MA recommendation folders
- **Search** — Tracks, Artists, Albums, Playlists
- **Similar tracks** — powered by Yandex rotor station
- **Lyrics** — fetched from Yandex Music API
- **Audio quality** — Efficient (AAC ~64 kbps) / Balanced (AAC ~192 kbps) / High (MP3 ~320 kbps) / Superb (FLAC lossless, with AES decryption for encraw transport)
- **My Wave radio** — infinite personalised radio with rotor feedback loop and cursor-based pagination
- **Multi-instance** — connect multiple Yandex Music accounts simultaneously

## Documentation

| Guide | Description |
|-------|-------------|
| [Configuration](docs/configuration.md) | Token, quality, My Wave, Liked Tracks settings |
| [Development](docs/development.md) | Dev setup, tests, linting, commit format |
| [Contributing](docs/contributing.md) | Bug reports, feature requests, pull requests |
| [Testing](docs/testing.md) | Running tests locally, CI pipeline, coverage |
| [Incident Management](docs/incident-management.md) | Labels, automated issue tracking, Copilot triage |
| [Docker Dev Environment](docs/dev-docker.md) | Run MA + provider locally without dependencies |

## References

- [Music Assistant](https://music-assistant.io/) — open-source music server by Marcel van der Veldt
- [Yandex Music](https://music.yandex.ru/) — streaming service by Yandex
- [yandex-music-api](https://github.com/MarshalX/yandex-music-api) — unofficial Python client by MarshalX

## License

[Apache 2.0](LICENSE) — see [CHANGELOG.md](CHANGELOG.md) for version history.
