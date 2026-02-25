---
title: Audio Quality
---

The provider supports four audio quality levels. The level is selected in the provider settings and applied globally to all tracks.

## Quality Levels

| Level | Format | Bitrate | Requirements |
|:--------|:-------|:--------|:-----------|
| **Efficient** | AAC | ~64 kbps | Any subscription |
| **Balanced** (default) | AAC | ~192 kbps | Any subscription |
| **High** | MP3 | ~320 kbps | Any subscription |
| **Superb** | FLAC | Lossless | Yandex Plus |

## Codec Selection

The provider requests the list of available variants for each track from the API and selects the best one matching the chosen level:

- **Superb** — FLAC is preferred; if unavailable — the best available format is used.
- **High** — MP3 320 kbps; if unavailable — any MP3 or best available.
- **Balanced** — AAC in the 128–256 kbps range; AAC preferred over MP3.
- **Efficient** — AAC at the lowest bitrate; if unavailable — MP3.

## Encrypted FLAC (encraw)

Lossless FLAC in Yandex Music is delivered encrypted via the `encraw` transport. The provider automatically:

1. Requests the encryption key and codec parameters from the API.
2. Decrypts the stream AES-CTR chunk by chunk in real time.
3. On connection drop, resumes download aligned to a block boundary (up to 3 retries).

This is completely transparent to the user — Music Assistant receives a clean FLAC stream.

## Subscription Requirements

The **Efficient**, **Balanced**, and **High** levels are available with any subscription (including no subscription).
The **Superb** level (FLAC Lossless) requires an active **Yandex Plus** subscription. Without it, the API does not return an encrypted stream, and the provider falls back to the best available format.
