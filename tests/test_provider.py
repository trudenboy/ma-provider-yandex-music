"""
Unit tests for YandexMusicProvider (provider.py).

These tests construct a partial provider instance via ``__new__`` (no
``__init__``), attach the attributes the method-under-test reads, and
exercise it directly. The pattern avoids the upstream Music Assistant
provider-init machinery which would otherwise drag in a real
``MusicAssistant`` instance.
"""

from __future__ import annotations

import logging
from typing import Any, cast
from unittest import mock

import pytest
from music_assistant_models.errors import LoginFailed, ResourceTemporarilyUnavailable

from music_assistant.models.music_provider import MusicProvider
from music_assistant.providers.yandex_music.constants import (
    CONF_BASE_URL,
    CONF_MANUAL_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_RESTRICTIVE_RATE_LIMITS,
    CONF_TOKEN,
    CONF_X_TOKEN,
    DEFAULT_BASE_URL,
    TRACK_BATCH_SIZE,
)
from music_assistant.providers.yandex_music.provider import YandexMusicProvider


def _make_provider() -> tuple[YandexMusicProvider, mock.AsyncMock]:
    """
    Return a YandexMusicProvider with a mocked Yandex API client.

    The provider is constructed without calling ``__init__`` so the upstream
    base-class init does not run. ``client`` is a property over ``_client``,
    so we assign the underlying attribute directly.
    """
    provider = YandexMusicProvider.__new__(YandexMusicProvider)
    mock_client = mock.AsyncMock()
    mock_client.user_id = 12345
    provider._client = mock_client
    provider.logger = mock.MagicMock()
    # ``instance_id`` and ``domain`` on the base class read from ``self.config``;
    # tests that need them attach a minimal config stub.
    return provider, mock_client


def _make_auth_init_provider(
    manual_token: str,
) -> tuple[YandexMusicProvider, mock.MagicMock, mock.MagicMock]:
    """Build the provider state needed to exercise manual-token initialization."""
    provider = YandexMusicProvider.__new__(YandexMusicProvider)
    provider._client = None
    provider.mass = mock.MagicMock()
    provider.logger = mock.MagicMock()
    provider.logger.level = logging.INFO
    values = {
        CONF_MANUAL_TOKEN: manual_token,
        CONF_BASE_URL: DEFAULT_BASE_URL,
        CONF_RESTRICTIVE_RATE_LIMITS: False,
    }
    provider.config = mock.MagicMock()
    provider.config.get_value = mock.MagicMock(
        side_effect=lambda key, default=None: values.get(key, default)
    )
    setup_values = {
        CONF_TOKEN: "old-token",
        CONF_X_TOKEN: "old-x-token",
        CONF_REFRESH_TOKEN: "old-refresh-token",
    }
    update_setup_data = mock.MagicMock()
    update_config_value = mock.MagicMock()
    untyped_provider = cast("Any", provider)
    untyped_provider.get_setup_value = mock.MagicMock(side_effect=setup_values.get)
    untyped_provider._update_setup_data = update_setup_data
    untyped_provider._update_config_value = update_config_value
    return provider, update_setup_data, update_config_value


async def test_manual_token_replacement_is_validated_then_promoted() -> None:
    """A working replacement supersedes and removes every old session credential."""
    provider, update_setup_data, update_config_value = _make_auth_init_provider("new-token")
    client = mock.AsyncMock()

    with (
        mock.patch(
            "music_assistant.providers.yandex_music.provider.YandexMusicClient",
            return_value=client,
        ) as client_class,
        mock.patch("music_assistant.providers.yandex_music.provider.YandexMusicStreamingManager"),
        mock.patch(
            "music_assistant.providers.yandex_music.provider.refresh_music_token",
            new=mock.AsyncMock(),
        ) as refresh_music_token,
    ):
        await provider.handle_async_init()

    supplied_token = client_class.call_args.args[0]
    assert supplied_token.get_secret() == "new-token"
    client.connect.assert_awaited_once()
    refresh_music_token.assert_not_awaited()
    update_setup_data.assert_has_calls(
        [
            mock.call(CONF_TOKEN, "new-token"),
            mock.call(CONF_X_TOKEN, None),
            mock.call(CONF_REFRESH_TOKEN, None),
        ]
    )
    update_config_value.assert_called_once_with(CONF_MANUAL_TOKEN, None, immediate=True)


async def test_invalid_manual_token_keeps_existing_setup_credentials() -> None:
    """A rejected replacement is discarded without damaging working setup data."""
    provider, update_setup_data, update_config_value = _make_auth_init_provider("invalid-token")
    client = mock.AsyncMock()
    client.connect.side_effect = LoginFailed("rejected")

    with (
        mock.patch(
            "music_assistant.providers.yandex_music.provider.YandexMusicClient",
            return_value=client,
        ) as client_class,
        mock.patch(
            "music_assistant.providers.yandex_music.provider.refresh_music_token",
            new=mock.AsyncMock(),
        ) as refresh_music_token,
        pytest.raises(LoginFailed, match="rejected"),
    ):
        await provider.handle_async_init()

    supplied_token = client_class.call_args.args[0]
    assert supplied_token.get_secret() == "invalid-token"
    assert client_class.call_count == 1
    refresh_music_token.assert_not_awaited()
    update_setup_data.assert_not_called()
    update_config_value.assert_called_once_with(CONF_MANUAL_TOKEN, None, immediate=True)


# -- M4: get_playlist_tracks must not abort on a single empty batch -----------


async def test_get_playlist_tracks_continues_on_empty_batch() -> None:
    """
    An empty batch mid-load must skip-and-continue, not discard prior batches.

    With ``TRACK_BATCH_SIZE`` of 50, a 150-track playlist resolves in 3 batches.
    If batch 2 transiently returns an empty list, the previous behavior raised
    ``ResourceTemporarilyUnavailable`` and threw away the 50 tracks already
    fetched from batch 1. The fixed behavior logs a warning and continues so
    the user sees a partial playlist rather than nothing.
    """
    provider, mock_client = _make_provider()

    # Build 3 batches of TRACK_BATCH_SIZE tracks (= 150 track refs total)
    total = TRACK_BATCH_SIZE * 3
    track_refs = [type("TR", (), {"track_id": str(i)})() for i in range(total)]
    playlist_obj = type(
        "PL",
        (),
        {
            "tracks": track_refs,
            "track_count": total,
        },
    )()
    mock_client.get_playlist = mock.AsyncMock(return_value=playlist_obj)

    batch1 = [type("YT", (), {"id": i})() for i in range(TRACK_BATCH_SIZE)]
    batch3 = [
        type("YT", (), {"id": i})() for i in range(2 * TRACK_BATCH_SIZE, 3 * TRACK_BATCH_SIZE)
    ]
    mock_client.get_tracks = mock.AsyncMock(side_effect=[batch1, [], batch3])

    # parse_track does heavy MA object construction; bypass it for this test
    # so we measure the batch-loop behavior, not the parser.
    with mock.patch(
        "music_assistant.providers.yandex_music.provider.parse_track",
        side_effect=lambda _self, t: t,
    ):
        fn: Any = YandexMusicProvider.get_playlist_tracks.__wrapped__  # type: ignore[attr-defined]
        result = await fn(provider, "12345:67")

    # 50 from batch 1 + 50 from batch 3 = 100 tracks; the empty batch 2 must
    # not abort the load.
    assert len(result) == 2 * TRACK_BATCH_SIZE
    assert mock_client.get_tracks.await_count == 3
    # The warning must still be emitted so operators can see the empty batch.
    assert any(
        "empty" in str(c.args).lower() or "empty" in str(c.kwargs).lower()
        for c in provider.logger.warning.call_args_list  # type: ignore[attr-defined]
    )


async def test_get_playlist_tracks_raises_only_when_every_batch_is_empty() -> None:
    """If every batch is empty, the existing terminal guard still fires."""
    provider, mock_client = _make_provider()

    total = TRACK_BATCH_SIZE * 2
    track_refs = [type("TR", (), {"track_id": str(i)})() for i in range(total)]
    playlist_obj = type(
        "PL",
        (),
        {
            "tracks": track_refs,
            "track_count": total,
        },
    )()
    mock_client.get_playlist = mock.AsyncMock(return_value=playlist_obj)
    mock_client.get_tracks = mock.AsyncMock(side_effect=[[], []])

    fn: Any = YandexMusicProvider.get_playlist_tracks.__wrapped__  # type: ignore[attr-defined]
    with pytest.raises(ResourceTemporarilyUnavailable):
        await fn(provider, "12345:67")


# -- M11: unload() must clear every per-session cache -------------------------


async def test_unload_clears_all_per_session_caches() -> None:
    """
    unload() must drop every state dict mirrored in handle_async_init().

    Without this, stale ``asyncio.Lock`` instances bound to the previous
    event loop survive a provider reload and break wave-session locking
    after a settings change.
    """
    provider = YandexMusicProvider.__new__(YandexMusicProvider)
    provider._client = None
    provider._streaming = None
    provider._wave_states = {"my_wave": mock.MagicMock()}
    provider._wave_bg_colors = {"img-key": "#abcdef"}
    provider._liked_albums_cache = (123.0, [])
    provider._audiobook_chapter_cache = {"book-1": (["track-1"], [1000])}
    provider._audiobook_play_ids = {"book-1": "play-id-1"}
    provider.logger = mock.MagicMock()

    with mock.patch.object(MusicProvider, "unload", new=mock.AsyncMock()):
        await provider.unload()

    # Cast through ``Any`` so mypy does not narrow these attributes to their
    # post-assignment types — assert against the runtime values after unload.
    state: Any = vars(provider)
    assert not state["_wave_states"]
    assert not state["_wave_bg_colors"]
    assert state["_liked_albums_cache"] is None
    assert not state["_audiobook_chapter_cache"]
    assert not state["_audiobook_play_ids"]
