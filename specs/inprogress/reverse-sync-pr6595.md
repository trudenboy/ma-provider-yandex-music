# Reverse-sync: upstream PR #6595

Ported from music-assistant/server#6595 into `yandex_music`.

## Summary

`BYPASS_THROTTLER` is replaced by request priorities: stream-URL refreshes run under `request_priority(RequestPriority.HIGH)`, which skips the block check and jitter but still takes a throttler slot; the restrictive-mode global concurrency cap is held only while a request is in flight.
