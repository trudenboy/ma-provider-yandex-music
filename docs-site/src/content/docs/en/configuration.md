---
title: Configuration
---

import { Steps } from '@astrojs/starlight/components';

## Step 1 — Get a token

The provider uses an OAuth token to authenticate with the Yandex Music API.

:::danger[Token security]
An OAuth token grants full access to your Yandex Music account. Do not share it with third parties or enter it on third-party websites. Store the token like a password.
:::

### Getting a token

1. Open the following link in your browser:
   **[oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d](https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d)**
2. Sign in to your Yandex account if prompted.
3. After authorization, the browser will redirect to a page with the token in the address bar — find the part that reads `access_token=XXXXXX`.
4. Copy the token value — the long string of letters and digits after `access_token=` and before the `&` character.

Alternative ways to obtain a token (Chrome/Firefox extension, Android APK, and others) are described in the [yandex-music-api documentation](https://yandex-music.readthedocs.io/en/main/token.html).

---

## Step 2 — Add the provider in Music Assistant
<Steps>
1. Open **Music Assistant → Settings → Music Providers**.
2. Click **"+ Add"** and select **Yandex Music**.
3. Paste the copied token into the **"Yandex Music Token"** field.
4. Select your preferred **audio quality** (see below).
5. Click **"Save"**.
6. MA will connect to Yandex Music and begin syncing your library.
</Steps>

---

## Parameters

| Parameter | Default | Description |
|:---------|:-------------|:---------|
| **Yandex Music Token** | — | OAuth authorization token. Required. |
| **Reset authorization** | — | Clears the saved token for re-authentication. |
| **Audio quality** | Balanced | Quality level: Efficient / Balanced / High / Superb. See [Audio quality](features/audio-quality/) for details. |
| **My Wave — max tracks** *(advanced)* | 150 | Number of tracks loaded for the My Wave playlist. Fewer → faster loading. Range: 10–1000. |
| **Liked — max tracks** *(advanced)* | 500 | Maximum tracks in the virtual "Liked" playlist. Higher values slow down loading. Range: 50–2000. |
| **API Base URL** *(advanced)* | `https://api.music.yandex.net` | Base API URL. Change only if Yandex changes the endpoint. |

Parameters marked *(advanced)* are shown in "Advanced settings" mode.

---

## If the token stops working

Tokens may expire after some time. Symptoms: the provider stops playing tracks or shows an authorization error.

**Solution:**
1. Open the Yandex Music provider settings in MA.
2. Click **"Reset authorization"**.
3. Get a new token following the instructions above (Step 1).
4. Enter the new token and click **"Save"**.
