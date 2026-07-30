# Reverse-sync: upstream PR #5010

Ported from music-assistant/server#5010 into `yandex_music`.

## Summary

Authenticate new and reconfigured instances through Music Assistant's guided setup
session. Users can choose Device Code or QR login and optionally retain the session
credentials needed for silent token refresh.

## Acceptance criteria

- Device Code and QR authentication run through `SetupSession`.
- Expired QR and device codes are refreshed without abandoning the setup flow.
- An abandoned login flow terminates after a fixed 15-minute lifetime.
- The flow stores a music token and only retains long-lived credentials when requested.
- QR rendering uses the pinned `segno` dependency.
- Existing token-refresh behavior remains covered by the full test suite.

## Test plan

Run `tests/test_setup_flow.py` and `tests/test_auth.py`, then the full repository quality gate.
