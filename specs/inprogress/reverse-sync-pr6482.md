# Reverse-sync: upstream PR #6482

Ported from music-assistant/server#6482 into `yandex_music`.

## Summary

Favorites become per-user and items can be disliked: `favorite` defaults to `None` instead of `False`, and metadata gains `last_musicbrainz_lookup`. Parser snapshots are updated.
