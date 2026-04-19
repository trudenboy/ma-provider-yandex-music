"""Unit tests for device_auth.py (OAuth Device Flow authentication)."""

from __future__ import annotations

from unittest import mock

import pytest
from music_assistant_models.errors import LoginFailed
from yandex_music.exceptions import DeviceAuthError, NetworkError

from music_assistant.providers.yandex_music.device_auth import perform_device_auth


def _make_device_code(
    user_code: str = "ABCD-1234",
    interval: int = 1,
    expires_in: int = 600,
) -> mock.MagicMock:
    """Build a fake DeviceCode object."""
    code = mock.MagicMock()
    code.device_code = "dev-code-xyz"
    code.user_code = user_code
    code.verification_url = "https://oauth.yandex.ru/device"
    code.interval = interval
    code.expires_in = expires_in
    return code


def _patch_client_async(client: mock.AsyncMock) -> mock._patch[mock.MagicMock]:
    """Patch ClientAsync to return our mocked client instance."""
    return mock.patch(
        "music_assistant.providers.yandex_music.device_auth.ClientAsync",
        return_value=client,
    )


def _patch_auth_helper(helper: mock.AsyncMock) -> mock._patch[mock.MagicMock]:
    """Patch AuthenticationHelper context manager."""
    return mock.patch(
        "music_assistant.providers.yandex_music.device_auth.AuthenticationHelper",
        return_value=helper,
    )


async def test_perform_device_auth_returns_token_when_user_confirms() -> None:
    """Device flow returns the access_token after the user confirms."""
    device = _make_device_code()
    token = mock.MagicMock(access_token="music-token-123")

    client = mock.AsyncMock()
    client.request_device_code = mock.AsyncMock(return_value=device)
    client.poll_device_token = mock.AsyncMock(return_value=token)

    helper = mock.AsyncMock()
    helper.__aenter__ = mock.AsyncMock(return_value=helper)
    helper.send_url = mock.MagicMock()
    helper.send_text = mock.MagicMock()

    with (
        _patch_client_async(client),
        _patch_auth_helper(helper),
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.asyncio.sleep",
            new=mock.AsyncMock(),
        ),
    ):
        result = await perform_device_auth(mock.MagicMock(), "session_1")

    assert result == "music-token-123"
    client.request_device_code.assert_awaited_once()
    client.poll_device_token.assert_awaited_with("dev-code-xyz")
    helper.send_url.assert_called_once_with("https://oauth.yandex.ru/device")
    helper.send_text.assert_called_once()
    assert "ABCD-1234" in helper.send_text.call_args.args[0]


async def test_perform_device_auth_polls_until_token_returned() -> None:
    """Device flow keeps polling while poll_device_token returns None."""
    device = _make_device_code()
    token = mock.MagicMock(access_token="music-token-456")

    client = mock.AsyncMock()
    client.request_device_code = mock.AsyncMock(return_value=device)
    client.poll_device_token = mock.AsyncMock(side_effect=[None, None, token])

    helper = mock.AsyncMock()
    helper.__aenter__ = mock.AsyncMock(return_value=helper)
    helper.send_url = mock.MagicMock()
    helper.send_text = mock.MagicMock()

    with (
        _patch_client_async(client),
        _patch_auth_helper(helper),
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.asyncio.sleep",
            new=mock.AsyncMock(),
        ),
    ):
        result = await perform_device_auth(mock.MagicMock(), "session_1")

    assert result == "music-token-456"
    assert client.poll_device_token.await_count == 3


async def test_perform_device_auth_timeout_raises_login_failed() -> None:
    """Device flow raises LoginFailed when expires_in elapses without confirmation."""
    device = _make_device_code(expires_in=2, interval=1)

    client = mock.AsyncMock()
    client.request_device_code = mock.AsyncMock(return_value=device)
    client.poll_device_token = mock.AsyncMock(return_value=None)

    helper = mock.AsyncMock()
    helper.__aenter__ = mock.AsyncMock(return_value=helper)
    helper.send_url = mock.MagicMock()
    helper.send_text = mock.MagicMock()

    # Simulate time advancing past the deadline by patching the loop's time.
    times = iter([100.0, 100.0, 1000.0])  # start, first-loop, deadline-exceeded check
    fake_loop = mock.MagicMock()
    fake_loop.time = lambda: next(times)

    with (
        _patch_client_async(client),
        _patch_auth_helper(helper),
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.asyncio.sleep",
            new=mock.AsyncMock(),
        ),
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.asyncio.get_running_loop",
            return_value=fake_loop,
        ),
        pytest.raises(LoginFailed, match="timed out"),
    ):
        await perform_device_auth(mock.MagicMock(), "session_1")


async def test_perform_device_auth_device_error_raises_login_failed() -> None:
    """A DeviceAuthError from the library is mapped to LoginFailed."""
    device = _make_device_code()

    client = mock.AsyncMock()
    client.request_device_code = mock.AsyncMock(return_value=device)
    client.poll_device_token = mock.AsyncMock(side_effect=DeviceAuthError("access_denied"))

    helper = mock.AsyncMock()
    helper.__aenter__ = mock.AsyncMock(return_value=helper)
    helper.send_url = mock.MagicMock()
    helper.send_text = mock.MagicMock()

    with (
        _patch_client_async(client),
        _patch_auth_helper(helper),
        mock.patch(
            "music_assistant.providers.yandex_music.device_auth.asyncio.sleep",
            new=mock.AsyncMock(),
        ),
        pytest.raises(LoginFailed, match="device auth error"),
    ):
        await perform_device_auth(mock.MagicMock(), "session_1")


async def test_perform_device_auth_network_error_raises_login_failed() -> None:
    """A NetworkError during request_device_code is mapped to LoginFailed."""
    client = mock.AsyncMock()
    client.request_device_code = mock.AsyncMock(side_effect=NetworkError("offline"))

    helper = mock.AsyncMock()
    helper.__aenter__ = mock.AsyncMock(return_value=helper)

    with (
        _patch_client_async(client),
        _patch_auth_helper(helper),
        pytest.raises(LoginFailed, match="Network error"),
    ):
        await perform_device_auth(mock.MagicMock(), "session_1")
