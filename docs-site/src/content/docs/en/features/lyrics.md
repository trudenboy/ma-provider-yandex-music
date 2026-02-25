---
title: Lyrics
---

The provider fetches lyrics directly from Yandex Music when viewing track details.

## Lyrics Types

| Type | Description |
|:----|:---------|
| **Synced (LRC)** | With timestamps — lyrics are highlighted in sync with the music when supported by the MA client |
| **Plain** | Used as a fallback when synced lyrics are unavailable |

## How It Works

1. MA requests track metadata via `ProviderFeature.TRACK_METADATA`.
2. The provider calls the Yandex Music API to fetch the lyrics.
3. If the API returns synced lyrics — they are stored as LRC.
4. If synced lyrics are unavailable — plain lyrics are stored.
5. If the API returns an error or empty response — metadata is returned without lyrics, without an error.

## Caching

Lyrics are cached along with track data. A repeated request for the same track does not hit the API again. The cache is cleared when the MA library is refreshed.
