# Reverse-sync: upstream PR #6382

Ported from music-assistant/server#6382 into `yandex_music`.

## Summary

Setup forms keep the raised `SetupFlowError` itself as the field error, so its localized message survives across providers and flow aborts.
