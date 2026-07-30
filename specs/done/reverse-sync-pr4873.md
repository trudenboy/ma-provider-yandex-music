# Reverse-sync: upstream PR #4873

Ported from music-assistant/server#4873 into `yandex_music`.

## Summary

Keep Yandex authentication copy aligned with Music Assistant's shared localization
conventions so common device-code wording is not duplicated by the provider.

## Acceptance criteria

- Authentication strings use the current setup-flow localization structure.
- Provider-specific login wording remains available in `strings.json`.
- Localization coverage tests pass.

## Test plan

Run `tests/test_localization.py`, then the full repository quality gate.
