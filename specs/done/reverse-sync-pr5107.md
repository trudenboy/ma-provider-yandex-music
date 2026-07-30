# Reverse-sync: upstream PR #5107

Ported from music-assistant/server#5107 into `yandex_music`.

## Summary

Expose My Wave from provider root browse as the same dynamic virtual playlist
returned by `get_playlist`. Marking the playlist dynamic lets Music Assistant
request additional tracks as its queue approaches the end.

## Acceptance criteria

- Root browse returns a `Playlist` for My Wave instead of a playable folder.
- The virtual My Wave playlist has `is_dynamic=True`.
- Other root browse folders and their ordering remain unchanged.
- Existing My Wave playback, pagination, presets, and feedback tests pass.

## Test plan

Run `tests/test_my_wave.py`, then the full repository quality gate.
