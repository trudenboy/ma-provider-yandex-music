# Reverse-sync: upstream PR #4946

Ported from music-assistant/server#4946 into `yandex_music`.

## Summary

Add cache-only subtitles to the Mood and Activity recommendation rows and use
the same deterministic hourly tag selection when their items are loaded. This
keeps row metadata aligned with served content without adding discovery-time
Yandex requests or mutable provider state.

## Acceptance criteria

- Warm tag caches produce localized Mood and Activity subtitles.
- Cold caches produce no subtitle and trigger no backend request.
- Tag selection is stable for a provider, category, and UTC hour.
- Mood and Activity item loading uses the same deterministic selector.
- Empty tag lists continue to return empty rows.
- No recommendation cache owned outside the provider instance is cleared.

## Test plan

Run `tests/test_recommendations.py`, then the full repository quality gate.
