# Reverse-sync: upstream PR #4487

Ported from music-assistant/server#4487 into `yandex_music`.

## Summary

Adopt Music Assistant's lazy recommendation-row API. Discovery now returns
nine ordered, empty descriptors without contacting Yandex; the new item
dispatcher loads only the row selected by the client.

## Acceptance criteria

- `get_recommendations` returns nine stable row IDs in the authored order.
- Descriptor discovery performs no Yandex backend calls.
- `get_recommendation_items` loads only the requested row helper.
- Mood and Activity choose their tag outside cached item helpers.
- Empty, unavailable, and unknown rows return an empty `UniqueList`.
- Existing recommendation parsers, caches, and error handling remain intact.

## Test plan

Run `tests/test_recommendations.py`, then the full repository quality gate.
