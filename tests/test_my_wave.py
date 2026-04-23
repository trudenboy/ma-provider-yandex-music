"""Tests for My Wave (Моя волна) browse and rotor feedback helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from music_assistant.providers.yandex_music.constants import (
    RADIO_TRACK_ID_SEP,
    ROTOR_STATION_MY_WAVE,
)
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
