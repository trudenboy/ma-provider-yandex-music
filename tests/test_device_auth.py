"""Unit tests for device_auth.py (ya-passport-auth Device Flow)."""

from __future__ import annotations

from unittest import mock

import pytest
from music_assistant_models.errors import LoginFailed
from ya_passport_auth import Credentials, DeviceCodeSession, SecretStr
from ya_passport_auth.exceptions import (
    DeviceCodeTimeoutError,
)
from ya_passport_auth.exceptions import (
    NetworkError as PassportNetworkError,
)

from music_assistant.providers.yandex_music.device_auth import perform_device_auth

# -- helpers -------------------------------------------------------------------


def _make_device_session(
    user_code: str = "ABCD-1234",
    verification_url: str = "https://oauth.yandex.ru/device",
    interval: int = 1,
    expires_in: int = 600,
) -> DeviceCodeSession:
    """Build a DeviceCodeSession for testing."""
    return DeviceCodeSession(
        device_code=SecretStr("dev-code-xyz"),
        user_code=user_code,
        verification_url=verification_url,
        expires_in=expires_in,
        interval=interval,
    )


def _make_credentials(
    x_token: str = "test_x_token",  # noqa: S107
    music_token: str | None = "test_music_token",  # noqa: S107
    refresh_token: str | None = "test_refresh_token",  # noqa: S107
) -> Credentials:
    """Build a Credentials dataclass for testing."""
    return Credentials(
        x_token=SecretStr(x_token),
        music_token=SecretStr(music_token) if music_token else None,
        refresh_token=SecretStr(refresh_token) if refresh_token else None,
    )


# -- perform_device_auth -------------------------------------------------------


async def test_perform_device_auth_returns_three_tokens() -> None:
    """Device flow returns (x_token, music_token, refresh_token)."""
    session = _make_device_session()
    creds = _make_credentials()
    mock_client = mock.AsyncMock()
    mock_client.start_device_login.return_value = session
    mock_client.poll_device_until_confirmed.return_value = creds

    mock_mass = mock.MagicMock()
    mock_mass.webserver.base_url = "http://ma.local:8095"
    mock_auth_helper = mock.AsyncMock()

    with (
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.PassportClient.create",
        ) as mock_create,
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.AuthenticationHelper",
            return_value=mock_auth_helper,
        ),
    ):
        mock_create.return_value.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_create.return_value.__aexit__ = mock.AsyncMock(return_value=False)

        x_token, music_token, refresh_token = await perform_device_auth(mock_mass, "session_1")

    assert x_token == "test_x_token"
    assert music_token == "test_music_token"
    assert refresh_token == "test_refresh_token"
    mock_client.start_device_login.assert_awaited_once()
    mock_client.poll_device_until_confirmed.assert_awaited_once_with(session)


async def test_perform_device_auth_serves_intermediate_page_and_cleans_up() -> None:
    """A temporary HTML page is registered on MA's webserver and unregistered after."""
    session = _make_device_session(
        user_code="WXYZ-9999",
        verification_url="https://oauth.yandex.ru/device",
    )
    creds = _make_credentials()
    mock_client = mock.AsyncMock()
    mock_client.start_device_login.return_value = session
    mock_client.poll_device_until_confirmed.return_value = creds

    mock_mass = mock.MagicMock()
    mock_mass.webserver.base_url = "http://ma.local:8095"
    mock_auth_helper = mock.AsyncMock()

    with (
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.PassportClient.create",
        ) as mock_create,
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.AuthenticationHelper",
            return_value=mock_auth_helper,
        ),
    ):
        mock_create.return_value.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_create.return_value.__aexit__ = mock.AsyncMock(return_value=False)

        await perform_device_auth(mock_mass, "session_1")

    expected_path = "/yandex_music/device_code/session_1"
    mock_mass.webserver.register_dynamic_route.assert_called_once()
    register_args = mock_mass.webserver.register_dynamic_route.call_args
    assert register_args.args[0] == expected_path
    assert register_args.args[2] == "GET"
    mock_mass.webserver.unregister_dynamic_route.assert_called_once_with(expected_path, "GET")
    mock_auth_helper.__aenter__.return_value.send_url.assert_called_once_with(
        f"http://ma.local:8095{expected_path}"
    )


async def test_perform_device_auth_route_handler_renders_code_and_url() -> None:
    """The registered route handler returns HTML containing the code + verification URL."""
    session = _make_device_session(
        user_code="ABCD-1234",
        verification_url="https://oauth.yandex.ru/device",
    )
    creds = _make_credentials()
    mock_client = mock.AsyncMock()
    mock_client.start_device_login.return_value = session
    mock_client.poll_device_until_confirmed.return_value = creds

    mock_mass = mock.MagicMock()
    mock_mass.webserver.base_url = "http://ma.local:8095"
    mock_auth_helper = mock.AsyncMock()

    with (
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.PassportClient.create",
        ) as mock_create,
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.AuthenticationHelper",
            return_value=mock_auth_helper,
        ),
    ):
        mock_create.return_value.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_create.return_value.__aexit__ = mock.AsyncMock(return_value=False)

        await perform_device_auth(mock_mass, "session_1")

    handler = mock_mass.webserver.register_dynamic_route.call_args.args[1]
    response = await handler(mock.MagicMock())
    body = response.text
    assert body is not None
    assert "ABCD-1234" in body
    assert "https://oauth.yandex.ru/device" in body
    assert response.content_type == "text/html"


async def test_perform_device_auth_timeout_raises_login_failed() -> None:
    """DeviceCodeTimeoutError from library is mapped to LoginFailed and the route is freed."""
    session = _make_device_session()
    mock_client = mock.AsyncMock()
    mock_client.start_device_login.return_value = session
    mock_client.poll_device_until_confirmed.side_effect = DeviceCodeTimeoutError("expired")

    mock_mass = mock.MagicMock()
    mock_mass.webserver.base_url = "http://ma.local:8095"
    mock_auth_helper = mock.AsyncMock()

    with (
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.PassportClient.create",
        ) as mock_create,
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.AuthenticationHelper",
            return_value=mock_auth_helper,
        ),
    ):
        mock_create.return_value.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_create.return_value.__aexit__ = mock.AsyncMock(return_value=False)

        with pytest.raises(LoginFailed, match="timed out"):
            await perform_device_auth(mock_mass, "session_1")

    mock_mass.webserver.unregister_dynamic_route.assert_called_once_with(
        "/yandex_music/device_code/session_1", "GET"
    )


async def test_perform_device_auth_ya_passport_error_raises_login_failed() -> None:
    """Generic YaPassportError from library is mapped to LoginFailed."""
    mock_client = mock.AsyncMock()
    mock_client.start_device_login.side_effect = PassportNetworkError("offline")

    mock_mass = mock.MagicMock()
    mock_auth_helper = mock.AsyncMock()

    with (
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.PassportClient.create",
        ) as mock_create,
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.AuthenticationHelper",
            return_value=mock_auth_helper,
        ),
    ):
        mock_create.return_value.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_create.return_value.__aexit__ = mock.AsyncMock(return_value=False)

        with pytest.raises(LoginFailed, match="device auth error"):
            await perform_device_auth(mock_mass, "session_1")


async def test_perform_device_auth_no_music_token_raises_login_failed() -> None:
    """Credentials without music_token raises LoginFailed."""
    session = _make_device_session()
    creds = _make_credentials(music_token=None)
    mock_client = mock.AsyncMock()
    mock_client.start_device_login.return_value = session
    mock_client.poll_device_until_confirmed.return_value = creds

    mock_mass = mock.MagicMock()
    mock_auth_helper = mock.AsyncMock()

    with (
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.PassportClient.create",
        ) as mock_create,
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.AuthenticationHelper",
            return_value=mock_auth_helper,
        ),
    ):
        mock_create.return_value.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_create.return_value.__aexit__ = mock.AsyncMock(return_value=False)

        with pytest.raises(LoginFailed, match="no music token"):
            await perform_device_auth(mock_mass, "session_1")


async def test_perform_device_auth_no_refresh_token_raises_login_failed() -> None:
    """Credentials without refresh_token raises LoginFailed."""
    session = _make_device_session()
    creds = _make_credentials(refresh_token=None)
    mock_client = mock.AsyncMock()
    mock_client.start_device_login.return_value = session
    mock_client.poll_device_until_confirmed.return_value = creds

    mock_mass = mock.MagicMock()
    mock_auth_helper = mock.AsyncMock()

    with (
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.PassportClient.create",
        ) as mock_create,
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.AuthenticationHelper",
            return_value=mock_auth_helper,
        ),
    ):
        mock_create.return_value.__aenter__ = mock.AsyncMock(return_value=mock_client)
        mock_create.return_value.__aexit__ = mock.AsyncMock(return_value=False)

        with pytest.raises(LoginFailed, match="no refresh token"):
            await perform_device_auth(mock_mass, "session_1")
