"""Unit tests for the provider config-flow entries (provider package init)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

from music_assistant.providers.yandex_music import get_config_entries
from music_assistant.providers.yandex_music.constants import (
    CONF_ACTION_CLEAR_AUTH,
    CONF_REFRESH_TOKEN,
    CONF_TOKEN,
    CONF_X_TOKEN,
)

if TYPE_CHECKING:
    from music_assistant_models.config_entries import ConfigValueType


async def test_get_config_entries_uses_manual_token_without_popup_actions() -> None:
    """Expose manual token setup while retaining stored refresh credentials."""
    values: dict[str, ConfigValueType] = {
        CONF_X_TOKEN: "stored-x",
        CONF_REFRESH_TOKEN: "stored-refresh",
    }

    entries = await get_config_entries(mock.MagicMock(), None, None, values)
    by_key = {entry.key: entry for entry in entries}

    assert "auth_device" not in by_key
    assert "auth_qr" not in by_key
    assert "remember_session" not in by_key
    assert CONF_TOKEN in by_key
    assert CONF_ACTION_CLEAR_AUTH in by_key
    assert by_key[CONF_X_TOKEN].value == "stored-x"
    assert by_key[CONF_REFRESH_TOKEN].value == "stored-refresh"
