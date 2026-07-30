# Reverse-sync: upstream PR #4793

Ported from music-assistant/server#4793 into `yandex_music`.

## Summary

Refresh Yandex Music parser snapshots for the metadata fields introduced by
music-assistant/server#4793. Provider runtime behavior is unchanged.

## Acceptance criteria

- Parser snapshots include `artist_entity_type`.
- Parser snapshots include `life_span`.
- Existing Yandex parser results otherwise remain unchanged.
- Parser tests pass without accepting unrelated snapshot changes.
- No provider runtime code changes.

## Test plan

Run `uv run --extra test pytest tests/test_parsers.py -q` and the full
repository quality gate.
