# Reverse-sync: upstream PR #5017

Ported from music-assistant/server#5017 into `yandex_music`.

## Summary

Move authentication out of the regular provider-options surface after guided setup,
and expose playback settings through the current provider instance configuration API.

## Acceptance criteria

- Authentication entries and actions do not appear in provider options.
- Setup credentials are read and rotated through setup data.
- Quality, limits, base URL, rate limits, and My Wave presets remain configurable.
- My Wave preset actions continue to persist and clear their draft fields.
- Existing configurations can fall back to Music Assistant's setup-data migration.

## Test plan

Run `tests/test_config_entries.py`, `tests/test_my_wave.py`, and the full repository quality gate.
