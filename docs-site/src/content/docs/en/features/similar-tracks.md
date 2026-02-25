---
title: Similar Tracks
---

The provider supports **Radio Mode** — a Music Assistant feature that builds a queue of tracks similar to the selected one.

## Where It Is Used

| Location | Action |
|:------|:---------|
| Context menu of any track | **Radio mode** — starts a queue of similar tracks |
| Any track source in MA | Available regardless of where the track came from |

## How It Works

Unlike a simple list of "similar" tracks by metadata, the provider uses the **Rotor API** from Yandex Music — the same machine learning engine behind My Wave personalization:

1. MA requests similar tracks for the selected track from the provider.
2. The provider creates a personal radio station based on that track via Rotor.
3. Rotor returns a batch of tracks selected by musical characteristics and your preferences.
4. The provider returns up to 25 tracks, excluding duplicates.

## Notes

- Recommendations are personalized — they take your listening history into account, not just track metadata similarity.
- If Rotor cannot find tracks for the given track — an empty list is returned (no error).
- Recommendation quality depends on the track being in the Yandex Music catalog and the account's listening history.
