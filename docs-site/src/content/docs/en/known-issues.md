---
title: Known Issues
---

## OAuth token expiration

**Symptoms:** The provider stops working after several days or weeks with no obvious configuration errors.

**Cause:** Yandex Music OAuth tokens have a limited lifetime. Once expired, the provider loses access to the API.

**Solution:** In the provider settings, click **"Reset authorization"**, get a new token by following the instructions on the [Configuration](configuration/) page, and enter it again.

---

## Connection drops during long sessions

**Symptoms:** Playback is interrupted or tracks fail to load after several hours of use.

**Cause:** The Yandex Music API closes long-lived connections. This is server-side behavior. The provider automatically re-establishes the connection on the next request (up to 3 retries with exponential backoff).

**Solution:** In most cases the provider recovers on its own. If not — restart Music Assistant.

---

## Geo-blocked playlists and tracks

**Symptoms:** Some playlists or tracks are unavailable, even though they open fine in the Yandex Music app.

**Cause:** Some content is restricted by geography or subscription type.

**Solution:** Content unavailable due to geo-blocking or subscription restrictions cannot be played through the provider. This is a Yandex Music limitation.

---

## FLAC unavailable without Yandex Plus subscription

**Symptoms:** When **Superb** quality is selected, tracks play at a lower quality or fail to play.

**Cause:** Lossless FLAC is only available with an active Yandex Plus subscription. Without it, the API does not return the encrypted FLAC stream.

**Solution:** Switch quality to **High** (MP3 320 kbps) or **Balanced** — these are available without a subscription. Alternatively, subscribe to Yandex Plus.
