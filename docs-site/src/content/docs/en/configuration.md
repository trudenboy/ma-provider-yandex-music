---
title: Configuration
---

## Authentication

Open **Music Assistant → Settings → Music Providers**, add **Yandex Music**, and choose a login method:

| Method | Description |
|:-------|:------------|
| **QR code** *(default)* | Scan the high-contrast QR code with the Yandex app and confirm the login. |
| **Device code** | Open the address shown in the yellow card, then enter the large code on that page. |
| **Token (manual)** | Paste an existing Yandex Music token. The token is validated before saving, but cannot refresh automatically. |

Expired QR and Device codes are renewed automatically. The complete interactive login stops after 15 minutes; start **Reconfigure** to try again.

**Remember session** applies to QR and Device Code login and is enabled by default. The provider stores the session credentials needed to refresh an expired music token automatically. When disabled, only the current music token is stored and you must reauthenticate after it expires. Manual-token login always stores only that token.

:::danger[Token security]
An OAuth token grants access to your Yandex Music account. Do not share it with third parties or enter it on third-party websites. Store the token like a password.
:::

## Reauthenticate or replace a token

To restart QR, Device Code, or manual-token login, open the menu for the relevant provider instance and select **Reconfigure**. You do not need to delete and recreate the provider.

Advanced settings also contain **Replace Yandex Music token**, a one-shot field for changing only the token. Leave it empty to keep the current credentials. When saved, the replacement is validated, moved to protected setup storage, and cleared from the field. An invalid replacement is discarded without overwriting the working stored credentials.

## Obtaining a token for manual login

Manual login is optional. If you use QR or Device Code, no token needs to be copied manually.

1. Open [Yandex OAuth](https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d).
2. Sign in and allow access when prompted.
3. Copy the value after `access_token=` and before the next `&` in the redirected URL.
4. Select **Token (manual)** in guided setup and paste the value.

## Parameters

| Parameter | Default | Description |
|:----------|:--------|:------------|
| **Audio quality** | Balanced | Efficient, Balanced, High, or Superb. See [Audio quality](features/audio-quality/) for details. |
| **My Wave maximum tracks** *(advanced)* | 150 | Tracks exposed by the My Wave playlist. Range: 10–1000. |
| **My Wave presets** *(advanced)* | None | Named presets built from optional diversity, mood, and language filters. Saved presets appear under **Radio → My Presets**. |
| **Liked Tracks maximum tracks** *(advanced)* | 200 | Tracks exposed by the Liked Tracks virtual playlist. Range: 50–2000. Higher values increase loading time and CAPTCHA risk. |
| **API Base URL** *(advanced)* | `https://api.music.yandex.net` | Change only if Yandex changes its API endpoint. |
| **Restrictive rate limits** *(advanced)* | Off | Safer request concurrency for VPS, VPN, and datacenter IPs. |
| **Replace Yandex Music token** *(advanced)* | Empty | Optional one-shot token replacement described above. |

Parameters marked *(advanced)* are displayed in **Show advanced settings** mode.
