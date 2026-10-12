# Reverse-sync: upstream PR #6887

Ported from music-assistant/server#6887 into `yandex_music`.

## Summary

Upstream enabled Ruff's `S311` (non-cryptographic random) rule. The provider uses `random` only for request jitter between liked-item batches and at initial sync, which needs no cryptographic strength, so those calls carry an explanatory `noqa: S311`. No behaviour change.
