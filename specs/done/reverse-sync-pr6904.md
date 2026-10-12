# Reverse-sync: upstream PR #6904

Ported from music-assistant/server#6904 into `yandex_music`.

## Summary

Upstream enabled Ruff's `S105` (hardcoded password) rule. The config-key constants `CONF_TOKEN`, `CONF_MANUAL_TOKEN`, `CONF_X_TOKEN`, `CONF_REFRESH_TOKEN` and the `METHOD_TOKEN` auth-method name are not secrets, so they carry an explanatory `noqa: S105`. No behaviour change.
