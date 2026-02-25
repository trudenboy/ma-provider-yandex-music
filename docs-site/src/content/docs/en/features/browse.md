---
title: Browse Catalog
---

The provider implements a full **Browse** experience — navigation through the Yandex Music catalog directly from Music Assistant.

## Browse Structure

```
Yandex Music
├── My Wave               ← personal infinite stream
├── Radio                 ← radio stations powered by Rotor
│   ├── Personal          ← your personal waves (Rotor dashboard)
│   ├── Featured waves    ← curated wave categories
│   ├── AI Sets           ← AI-generated wave collections
│   ├── Genres
│   ├── Mood
│   ├── Activity
│   ├── Era
│   └── Local
├── For You               ← curated picks
│   ├── Picks             ← by mood, activity, era, genre
│   └── Mixes             ← seasonal playlists
├── Collection            ← your personal library
│   ├── Liked             ← virtual playlist of liked tracks
│   ├── My Artists
│   ├── My Albums
│   └── My Playlists
├── Chart                 ← Yandex Music top tracks
├── New Releases          ← fresh albums and singles
└── New Playlists         ← fresh playlists
```

Section names automatically switch between Russian and English depending on the locale setting in Music Assistant.

## Section Descriptions

### My Wave

A personal infinite stream of tracks powered by the Rotor API. Loaded in batches, duplicates are automatically filtered out. See [My Wave](my-wave/) for details.

### Radio

Yandex Music radio stations powered by the Rotor engine. Each station is an infinite stream personalized by the selected parameter. See [Radio](radio/) for details.

### For You — Picks and Mixes

Curated and algorithmic playlists organized by tags (mood, activity, era, genre) and seasons. Tags are discovered dynamically via the Landing API — empty categories are hidden automatically. See [Picks and Mixes](picks-and-mixes/) for details.

### Collection

Your personal library: liked tracks (virtual playlist with a limit), artists, albums, and playlists. Likes sync bidirectionally — you can like or unlike directly from MA.

### Chart, New Releases, New Playlists

Up-to-date selections from the Yandex Music catalog, cached for 1 hour.
