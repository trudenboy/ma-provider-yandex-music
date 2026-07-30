# Reverse-sync: upstream PR #5030

Ported from music-assistant/server#5030 into `yandex_music`.

## Summary

Remove the Device and QR popup authentication actions after Music Assistant
retired its shared popup helper. New installations authenticate by entering a
Yandex Music token in advanced settings. Existing stored x-token and refresh
token values remain hidden and continue to support silent credential refresh.

## Acceptance criteria

- Config entries no longer expose Device, QR, remember-session, or session-id
  controls.
- Manual music-token entry and clear-auth remain available.
- Stored x-token and refresh-token values are preserved by the config flow.
- Token validation and refresh helpers retain their error mapping and redaction.
- No provider or test code imports `music_assistant.helpers.auth`.

## Test plan

Run the auth, config-entry, and localization tests, then the full repository
quality gate.
