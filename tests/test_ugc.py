"""Regression tests for user-uploaded Yandex Music tracks."""

from __future__ import annotations

from inspect import unwrap
from typing import TYPE_CHECKING, cast
from unittest.mock import MagicMock

import pytest
from music_assistant_models.errors import InvalidDataError
from yandex_music import Track as YandexTrack

from music_assistant.providers.yandex_music.parsers import (
    parse_track,
    parse_ugc_artist,
)
from music_assistant.providers.yandex_music.provider import YandexMusicProvider

from .conftest import DE_JSON_CLIENT

if TYPE_CHECKING:
    from .conftest import ProviderStub


def make_ugc_track(artist_name: str | None) -> YandexTrack:
    """Construct a UGC track using the real Yandex Music deserializer."""
    obj = YandexTrack.de_json(
        {
            "id": "7c60a004-bd7a-4538-b852-8c934d935ce8",
            "title": "Take Me Deeper",
            "durationMs": 259000,
            "available": True,
            "trackSource": "UGC",
            "artists": [{"name": artist_name}],
            "albums": [],
        },
        DE_JSON_CLIENT,
    )
    assert obj is not None
    return obj


@pytest.mark.parametrize(
    "name",
    ["Nico Voss", "Исполнитель", "AC/DC", "Björk", "A & B"],
)
def test_ugc_artist_stable_identity(provider_stub: ProviderStub, name: str) -> None:
    """Repeated parsing must produce the same virtual artist identity."""
    provider = cast("YandexMusicProvider", provider_stub)

    first = parse_ugc_artist(provider, name)
    second = parse_ugc_artist(provider, name)

    assert first.item_id == second.item_id
    assert first.name == name
    assert first.item_id.startswith("ugc_artist:")
    assert first.provider == provider_stub.instance_id

    mapping = next(iter(first.provider_mappings))
    assert mapping.item_id == first.item_id
    assert mapping.url is None


def test_ugc_artist_names_do_not_collide(provider_stub: ProviderStub) -> None:
    """Different artist names must have different provider item IDs."""
    provider = cast("YandexMusicProvider", provider_stub)

    first = parse_ugc_artist(provider, "Nico Voss")
    second = parse_ugc_artist(provider, "Nico Voss 2")

    assert first.item_id != second.item_id


def test_ugc_track_with_name_only_artist(provider_stub: ProviderStub) -> None:
    """A UGC track without a catalog artist ID must be importable."""
    provider = cast("YandexMusicProvider", provider_stub)

    result = parse_track(provider, make_ugc_track("Nico Voss"))

    assert result.name == "Take Me Deeper"
    assert result.duration == 259
    assert len(result.artists) == 1
    assert result.artists[0].name == "Nico Voss"
    assert result.artists[0].item_id == "ugc_artist:Nico%20Voss"
    assert result.album is None


@pytest.mark.parametrize("name", ["", "   ", None])
def test_ugc_artist_without_name_is_rejected(provider_stub: ProviderStub, name: str | None) -> None:
    """An unnamed UGC artist must not produce an invalid virtual ID."""
    provider = cast("YandexMusicProvider", provider_stub)

    with pytest.raises(InvalidDataError):
        parse_track(provider, make_ugc_track(name))


@pytest.mark.asyncio
async def test_get_ugc_artist_does_not_call_yandex_api(
    provider_stub: ProviderStub,
) -> None:
    """Virtual artists must be resolved without Yandex API requests."""
    provider = cast("YandexMusicProvider", provider_stub)
    client = MagicMock()
    provider_stub.client = client

    # Bypass @use_cache to test the provider method directly.
    get_artist = unwrap(YandexMusicProvider.get_artist)

    result = await get_artist(provider, "ugc_artist:Nico%20Voss")

    assert result.name == "Nico Voss"
    assert result.item_id == "ugc_artist:Nico%20Voss"
    assert result.provider == provider_stub.instance_id

    client.get_artist.assert_not_called()
    client.get_artist_about.assert_not_called()
