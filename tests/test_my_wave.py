"""Tests for My Wave (Моя волна) browse and rotor feedback helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest
from music_assistant_models.enums import MediaType
from music_assistant_models.media_items import ProviderMapping
from music_assistant_models.media_items import Track as MATrack

from music_assistant.providers.yandex_music.constants import (
    RADIO_TRACK_ID_SEP,
    ROTOR_STATION_MY_WAVE,
)
from music_assistant.providers.yandex_music.parsers import parse_playlist
from music_assistant.providers.yandex_music.provider import (
    YandexMusicProvider,
    _parse_radio_item_id,
    _WaveState,
)


def test_parse_radio_item_id_plain_track_id() -> None:
    """Plain track_id returns (track_id, None)."""
    assert _parse_radio_item_id("12345") == ("12345", None)
    assert _parse_radio_item_id("0") == ("0", None)


def test_parse_radio_item_id_composite() -> None:
    """Composite track_id@station_id returns (track_id, station_id)."""
    assert _parse_radio_item_id(f"12345{RADIO_TRACK_ID_SEP}{ROTOR_STATION_MY_WAVE}") == (
        "12345",
        ROTOR_STATION_MY_WAVE,
    )
    assert _parse_radio_item_id("99@user:custom") == ("99", "user:custom")


def test_wave_state_has_session_fields() -> None:
    """_WaveState exposes session_id, playlist_next_cursor, prefetched, settings."""
    state = _WaveState()
    # Session-based rotor API identifiers
    assert state.session_id is None
    # Legacy stations-based identifier retained during migration
    assert state.batch_id is None
    # Pagination cursor for virtual playlist pages
    assert state.playlist_next_cursor is None
    # Prefetch buffer for future-batch tracks
    assert state.prefetched == []
    # Persistent station settings (diversity/moodEnergy/language)
    assert state.settings == {}
    # Once-per-session flag
    assert state.radio_started_sent is False


def test_wave_state_is_per_instance_isolated() -> None:
    """Each _WaveState has its own mutable containers (no shared class state)."""
    a, b = _WaveState(), _WaveState()
    a.seen_track_ids.add("1")
    a.prefetched.append("x")
    a.settings["diversity"] = "discover"
    assert b.seen_track_ids == set()
    assert b.prefetched == []
    assert b.settings == {}


# -- _fetch_rotor_session_batch (session-API helper) --------------------------


@pytest.mark.asyncio
async def test_fetch_rotor_session_batch_starts_session_on_first_call() -> None:
    """First call creates a rotor session and records session_id + batch_id on wave state."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_new = AsyncMock(
        return_value=("sess_1", ["track1", "track2"], "batch_a")
    )
    provider.client.rotor_session_tracks = AsyncMock()
    wave = _WaveState()

    tracks, batch_id = await YandexMusicProvider._fetch_rotor_session_batch(
        provider, wave, ROTOR_STATION_MY_WAVE
    )

    provider.client.rotor_session_new.assert_awaited_once_with(ROTOR_STATION_MY_WAVE, settings=None)
    provider.client.rotor_session_tracks.assert_not_awaited()
    assert wave.session_id == "sess_1"
    assert wave.batch_id == "batch_a"
    assert tracks == ["track1", "track2"]
    assert batch_id == "batch_a"


@pytest.mark.asyncio
async def test_fetch_rotor_session_batch_passes_wave_settings_to_session_new() -> None:
    """Session creation forwards wave.settings (diversity/moodEnergy/language) as seeds."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_new = AsyncMock(return_value=("s", [], "b"))
    wave = _WaveState()
    wave.settings = {"diversity": "discover", "moodEnergy": "calm"}

    await YandexMusicProvider._fetch_rotor_session_batch(provider, wave, ROTOR_STATION_MY_WAVE)

    _, kwargs = provider.client.rotor_session_new.await_args
    assert kwargs["settings"] == {"diversity": "discover", "moodEnergy": "calm"}


@pytest.mark.asyncio
async def test_fetch_rotor_session_batch_paginates_via_session_tracks_after_first_call() -> None:
    """Once session_id is set, subsequent calls use rotor_session_tracks with last_track_id."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_new = AsyncMock()
    provider.client.rotor_session_tracks = AsyncMock(return_value=(["t3"], "batch_b"))
    wave = _WaveState()
    wave.session_id = "sess_1"
    wave.last_track_id = "42"

    tracks, _batch_id = await YandexMusicProvider._fetch_rotor_session_batch(
        provider, wave, ROTOR_STATION_MY_WAVE
    )

    provider.client.rotor_session_new.assert_not_awaited()
    provider.client.rotor_session_tracks.assert_awaited_once_with("sess_1", current_track_id="42")
    assert wave.batch_id == "batch_b"
    assert tracks == ["t3"]


@pytest.mark.asyncio
async def test_fetch_rotor_session_batch_returns_empty_when_session_new_fails() -> None:
    """When session creation returns None session_id, wave is not mutated and result is empty."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_new = AsyncMock(return_value=(None, [], None))
    wave = _WaveState()

    tracks, batch_id = await YandexMusicProvider._fetch_rotor_session_batch(
        provider, wave, ROTOR_STATION_MY_WAVE
    )

    assert wave.session_id is None
    assert tracks == []
    assert batch_id is None


@pytest.mark.asyncio
async def test_fetch_rotor_session_batch_works_with_track_seed_station() -> None:
    """get_similar_tracks uses station 'track:{id}' — same session machinery."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_new = AsyncMock(return_value=("s", ["t"], "b"))
    wave = _WaveState()

    await YandexMusicProvider._fetch_rotor_session_batch(provider, wave, "track:9999")

    provider.client.rotor_session_new.assert_awaited_once_with("track:9999", settings=None)
    assert wave.session_id == "s"


# -- wave-mode preset routing -------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_rotor_session_batch_resolves_wave_mode_preset_settings() -> None:
    """A station key like 'user:onyourwave#discover' translates to settingDiversity=discover."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_new = AsyncMock(return_value=("sess_1", [], "batch_a"))
    wave = _WaveState()

    await YandexMusicProvider._fetch_rotor_session_batch(
        provider, wave, f"{ROTOR_STATION_MY_WAVE}#discover"
    )

    provider.client.rotor_session_new.assert_awaited_once_with(
        ROTOR_STATION_MY_WAVE, settings={"diversity": "discover"}
    )
    assert wave.session_id == "sess_1"


@pytest.mark.asyncio
async def test_fetch_rotor_session_batch_preset_merges_with_explicit_wave_settings() -> None:
    """Explicit wave.settings overrides preset settings on the same key."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_new = AsyncMock(return_value=("s", [], "b"))
    wave = _WaveState()
    wave.settings = {"diversity": "popular"}  # overrides preset

    await YandexMusicProvider._fetch_rotor_session_batch(
        provider, wave, f"{ROTOR_STATION_MY_WAVE}#discover"
    )

    _, kwargs = provider.client.rotor_session_new.await_args
    # wave.settings wins over preset
    assert kwargs["settings"] == {"diversity": "popular"}


@pytest.mark.asyncio
async def test_fetch_rotor_session_batch_unknown_preset_passes_station_through() -> None:
    """Unknown '#<x>' keys leave station_id alone so the server returns an error naturally."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_new = AsyncMock(return_value=(None, [], None))
    wave = _WaveState()

    await YandexMusicProvider._fetch_rotor_session_batch(
        provider, wave, f"{ROTOR_STATION_MY_WAVE}#does_not_exist"
    )

    # Base station still stripped; empty settings (no preset matched).
    provider.client.rotor_session_new.assert_awaited_once_with(ROTOR_STATION_MY_WAVE, settings=None)


# -- _parse_my_wave_track with explicit station_key --------------------------


# -- prefetch next batch (P6) -------------------------------------------------


@pytest.mark.asyncio
async def test_prefetch_rotor_session_fills_prefetched_when_idle() -> None:
    """With an active session and no prefetched tracks, fills wave.prefetched."""
    provider = Mock(spec=YandexMusicProvider)
    wave = _WaveState()
    wave.session_id = "sess_1"
    provider._wave_states = {ROTOR_STATION_MY_WAVE: wave}
    provider._fetch_rotor_session_batch = AsyncMock(return_value=(["t1", "t2"], "batch_b"))

    await YandexMusicProvider._prefetch_rotor_session(provider, ROTOR_STATION_MY_WAVE)

    assert wave.prefetched == ["t1", "t2"]


@pytest.mark.asyncio
async def test_prefetch_rotor_session_noop_without_session() -> None:
    """Prefetch does nothing when the station has no active session_id."""
    provider = Mock(spec=YandexMusicProvider)
    wave = _WaveState()
    provider._wave_states = {ROTOR_STATION_MY_WAVE: wave}
    provider._fetch_rotor_session_batch = AsyncMock()

    await YandexMusicProvider._prefetch_rotor_session(provider, ROTOR_STATION_MY_WAVE)

    provider._fetch_rotor_session_batch.assert_not_awaited()
    assert wave.prefetched == []


@pytest.mark.asyncio
async def test_prefetch_rotor_session_noop_when_already_prefilled() -> None:
    """Prefetch skips work when wave.prefetched already has items (avoid rate burn)."""
    provider = Mock(spec=YandexMusicProvider)
    wave = _WaveState()
    wave.session_id = "sess_1"
    wave.prefetched = ["existing_track"]
    provider._wave_states = {ROTOR_STATION_MY_WAVE: wave}
    provider._fetch_rotor_session_batch = AsyncMock()

    await YandexMusicProvider._prefetch_rotor_session(provider, ROTOR_STATION_MY_WAVE)

    provider._fetch_rotor_session_batch.assert_not_awaited()


# -- rotor feedback on library_add (P5) ---------------------------------------


@pytest.mark.asyncio
async def test_library_add_track_from_wave_also_sends_rotor_like() -> None:
    """library_add for a track from a wave session sends both users.like and rotor.like."""
    provider = Mock(spec=YandexMusicProvider)
    provider.instance_id = "yandex_music_instance"
    provider.logger = Mock()
    provider.client = AsyncMock()
    provider.client.like_track = AsyncMock(return_value=True)
    composite = f"12345{RADIO_TRACK_ID_SEP}{ROTOR_STATION_MY_WAVE}"
    provider._get_provider_item_id = Mock(return_value=composite)
    # Share a session so like is routed to rotor_session_feedback
    wave = _WaveState()
    wave.session_id = "sess_1"
    wave.batch_id = "batch_a"
    provider._wave_states = {ROTOR_STATION_MY_WAVE: wave}
    provider._get_wave_state = Mock(return_value=wave)
    provider._send_wave_feedback = AsyncMock(return_value=True)

    item = MATrack(
        item_id=composite,
        provider="yandex_music_instance",
        name="Test",
        provider_mappings={
            ProviderMapping(
                item_id=composite,
                provider_domain="yandex_music",
                provider_instance="yandex_music_instance",
            )
        },
    )
    item.media_type = MediaType.TRACK

    result = await YandexMusicProvider.library_add(provider, item)

    assert result is True
    provider.client.like_track.assert_awaited_once_with("12345")
    provider._send_wave_feedback.assert_awaited_once()
    args, kwargs = provider._send_wave_feedback.await_args
    assert args[0] is wave
    assert args[1] == ROTOR_STATION_MY_WAVE
    assert args[2] == "like"
    assert kwargs == {"track_id": "12345"}


@pytest.mark.asyncio
async def test_library_add_track_without_station_skips_rotor_feedback() -> None:
    """Plain track_id (no station suffix) does NOT trigger rotor feedback."""
    provider = Mock(spec=YandexMusicProvider)
    provider.instance_id = "yandex_music_instance"
    provider.logger = Mock()
    provider.client = AsyncMock()
    provider.client.like_track = AsyncMock(return_value=True)
    provider._get_provider_item_id = Mock(return_value="12345")
    provider._send_wave_feedback = AsyncMock()

    item = MATrack(
        item_id="12345",
        provider="yandex_music_instance",
        name="Test",
        provider_mappings={
            ProviderMapping(
                item_id="12345",
                provider_domain="yandex_music",
                provider_instance="yandex_music_instance",
            )
        },
    )
    item.media_type = MediaType.TRACK

    await YandexMusicProvider.library_add(provider, item)

    provider.client.like_track.assert_awaited_once_with("12345")
    provider._send_wave_feedback.assert_not_awaited()


# -- user wave presets (P8) ---------------------------------------------------


def test_get_user_wave_presets_parses_valid_json_list() -> None:
    """Valid JSON list is parsed into preset dicts, name is required."""
    provider = Mock(spec=YandexMusicProvider)
    provider.config = Mock()
    provider.config.get_value = Mock(
        return_value=(
            '[{"name": "Morning", "diversity": "discover", "moodEnergy": "calm"}, '
            '{"name": "Evening", "language": "russian"}]'
        )
    )
    provider.logger = Mock()

    result = YandexMusicProvider._get_user_wave_presets(provider)

    assert len(result) == 2
    assert result[0]["name"] == "Morning"
    assert result[0]["diversity"] == "discover"
    assert result[0]["moodEnergy"] == "calm"
    assert result[1]["name"] == "Evening"
    assert result[1]["language"] == "russian"


def test_get_user_wave_presets_returns_empty_for_empty_string() -> None:
    """Empty config → empty list (no presets configured)."""
    provider = Mock(spec=YandexMusicProvider)
    provider.config = Mock()
    provider.config.get_value = Mock(return_value="")
    provider.logger = Mock()

    assert YandexMusicProvider._get_user_wave_presets(provider) == []


def test_get_user_wave_presets_drops_entries_without_name() -> None:
    """Entries lacking a name are silently skipped, not crashing."""
    provider = Mock(spec=YandexMusicProvider)
    provider.config = Mock()
    provider.config.get_value = Mock(return_value='[{"diversity": "discover"}, {"name": "Valid"}]')
    provider.logger = Mock()

    result = YandexMusicProvider._get_user_wave_presets(provider)

    assert len(result) == 1
    assert result[0]["name"] == "Valid"


def test_get_user_wave_presets_handles_invalid_json() -> None:
    """Malformed JSON → empty list + warning logged."""
    provider = Mock(spec=YandexMusicProvider)
    provider.config = Mock()
    provider.config.get_value = Mock(return_value="not json {{{")
    provider.logger = Mock()

    result = YandexMusicProvider._get_user_wave_presets(provider)

    assert result == []
    provider.logger.warning.assert_called_once()


def test_parse_playlist_is_dynamic_flag_propagates() -> None:
    """parse_playlist honours is_dynamic=True so feed autoplaylists skip MA cache."""
    provider = Mock(spec=YandexMusicProvider)
    provider.instance_id = "yandex_music_instance"
    provider.domain = "yandex_music"
    provider.client = Mock()
    provider.client.user_id = 12345

    playlist_obj = Mock()
    playlist_obj.owner = Mock(uid=67890, name="Яндекс")
    playlist_obj.kind = 42
    playlist_obj.title = "Плейлист дня"
    playlist_obj.description = None
    playlist_obj.cover = None
    playlist_obj.track_count = 50
    playlist_obj.modified = None
    playlist_obj.created = None
    playlist_obj.tags = []

    result_dynamic = parse_playlist(provider, playlist_obj, is_dynamic=True)
    result_static = parse_playlist(provider, playlist_obj)

    assert result_dynamic.is_dynamic is True
    assert result_static.is_dynamic is False


def test_parse_my_wave_track_uses_provided_station_key_for_item_id() -> None:
    """_parse_my_wave_track stamps the supplied station_key on composite item_id."""
    # Build a minimal provider instance with the attributes _parse_my_wave_track
    # reads; don't use Mock(spec=...) because we call the real method.
    provider = Mock(spec=YandexMusicProvider)
    provider.instance_id = "yandex_music_instance"
    provider.logger = Mock()

    # Fake yandex track object
    yt = type("YTrack", (), {"id": "12345", "track_id": "12345"})()

    # Return a minimal MA Track from parse_track; _parse_my_wave_track rewrites
    # its item_id in-place to the composite form.
    base_track = MATrack(
        item_id="12345",
        provider="yandex_music_instance",
        name="Test",
        provider_mappings={
            ProviderMapping(
                item_id="12345",
                provider_domain="yandex_music",
                provider_instance="yandex_music_instance",
            )
        },
    )
    with patch(
        "music_assistant.providers.yandex_music.provider.parse_track",
        return_value=base_track,
    ):
        station_key = f"{ROTOR_STATION_MY_WAVE}#discover"
        seen: set[str] = set()
        result = YandexMusicProvider._parse_my_wave_track(
            provider, yt, seen, station_key=station_key
        )

    assert result is not None
    assert result.item_id == f"12345{RADIO_TRACK_ID_SEP}{station_key}"
    # And round-trip via _parse_radio_item_id
    assert _parse_radio_item_id(result.item_id) == ("12345", station_key)
    assert "12345" in seen


# -- _send_wave_feedback (session vs. stations API router) ---------------------


@pytest.mark.asyncio
async def test_send_wave_feedback_uses_session_api_when_session_id_present() -> None:
    """When wave.session_id is set, feedback is routed to rotor_session_feedback."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_feedback = AsyncMock(return_value=True)
    provider.client.send_rotor_station_feedback = AsyncMock()
    wave = _WaveState()
    wave.session_id = "sess_1"
    wave.batch_id = "batch_a"

    result = await YandexMusicProvider._send_wave_feedback(
        provider, wave, "user:onyourwave", "trackStarted", track_id="100"
    )

    assert result is True
    provider.client.rotor_session_feedback.assert_awaited_once_with(
        "sess_1", "trackStarted", track_id="100", total_played_seconds=None, batch_id="batch_a"
    )
    provider.client.send_rotor_station_feedback.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_wave_feedback_falls_back_to_stations_api_without_session() -> None:
    """When wave.session_id is None, feedback is routed to the old stations endpoint."""
    provider = Mock(spec=YandexMusicProvider)
    provider.client = AsyncMock()
    provider.client.rotor_session_feedback = AsyncMock()
    provider.client.send_rotor_station_feedback = AsyncMock(return_value=True)
    wave = _WaveState()
    wave.batch_id = "batch_a"

    result = await YandexMusicProvider._send_wave_feedback(
        provider, wave, "genre:rock", "skip", track_id="9", total_played_seconds=7
    )

    assert result is True
    provider.client.send_rotor_station_feedback.assert_awaited_once_with(
        "genre:rock", "skip", track_id="9", total_played_seconds=7, batch_id="batch_a"
    )
    provider.client.rotor_session_feedback.assert_not_awaited()
