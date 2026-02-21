[← Back to README](../README.md)

# Configuration

All settings are accessible via **Settings → Music Sources → Yandex Music**.

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `token` | Secure string | — | Yandex Music OAuth token. Required for authentication. See below for how to obtain it. |
| `quality` | String (enum) | `balanced` | Preferred audio quality. See [Quality Options](#quality-options) below. |
| `stream_buffer_mb` | Integer (1–64) | `8` | Memory buffer (MB) for encrypted FLAC streaming. Larger values reduce stalls on slow connections (~45 s of FLAC per 8 MB). Advanced. |
| `my_wave_max_tracks` | Integer (10–1000) | `150` | Maximum tracks to fetch for My Wave playlist. Lower values load faster. Advanced. |
| `liked_tracks_max_tracks` | Integer (50–5000) | `500` | Maximum tracks shown in Liked Tracks virtual playlist. Advanced. |
| `base_url` | String | `https://api.music.yandex.net` | API endpoint base URL. Change only if Yandex updates their endpoint. Advanced. |

### Quality Options

| Value | Label | Format | Bitrate |
|-------|-------|--------|---------|
| `efficient` | Efficient | AAC | ~64 kbps |
| `balanced` | Balanced | AAC | ~192 kbps |
| `high` | High | MP3 | ~320 kbps |
| `superb` | Superb | FLAC | Lossless |

## Obtaining a Token

Yandex Music requires an OAuth token. The provider documentation at
<https://music-assistant.io/music-providers/yandex-music/> explains how to obtain one.

## Actions

| Action | Description |
|--------|-------------|
| Reset authentication | Clears the stored token, allowing you to re-enter credentials. |
