"""Yandex Music OAuth Device Flow authentication.

Alternative entry point to QR auth: the user opens a verification URL on any
device, types a short code shown by Music Assistant, and the provider polls
Yandex until the user confirms. Returns only a music token — Device Flow does
not yield an x_token, so auto-refresh on token expiry is not possible.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from music_assistant_models.errors import LoginFailed
from yandex_music import ClientAsync
from yandex_music.exceptions import DeviceAuthError, NetworkError

from music_assistant.helpers.auth import AuthenticationHelper

if TYPE_CHECKING:
    from music_assistant import MusicAssistant

_LOGGER = logging.getLogger(__name__)


async def perform_device_auth(mass: MusicAssistant, session_id: str) -> str:
    """Perform Yandex OAuth Device Flow and return a music token.

    Asks Yandex for a device code, presents the verification URL and user code
    in the MA frontend, then polls until the user confirms or the code expires.

    :return: Music access token string suitable for ``CONF_TOKEN``.
    :raises LoginFailed: On timeout, user denial, or any device-flow error.
    """
    try:
        client = ClientAsync()
        device = await client.request_device_code()

        # AuthenticationHelper can only open one URL — append the user code
        # as a query param so the verification page can pre-fill it (and so
        # the user can read it from the address bar if it doesn't).
        url = f"{device.verification_url}?user_code={device.user_code}"
        _LOGGER.info(
            "Device flow started: open %s and enter code %s (expires in %ss)",
            device.verification_url,
            device.user_code,
            device.expires_in,
        )

        async with AuthenticationHelper(mass, session_id) as auth_helper:
            auth_helper.send_url(url)

            interval = max(device.interval, 1)
            deadline = asyncio.get_running_loop().time() + device.expires_in
            while True:
                if asyncio.get_running_loop().time() >= deadline:
                    raise LoginFailed("Device authentication timed out. Please try again.")
                await asyncio.sleep(interval)
                token = await client.poll_device_token(device.device_code)
                if token is not None:
                    _LOGGER.debug("Device flow complete, obtained music token")
                    access_token: str = token.access_token
                    return access_token

    except DeviceAuthError as err:
        raise LoginFailed(f"Yandex device auth error: {err}") from err
    except NetworkError as err:
        raise LoginFailed(f"Network error during device auth: {err}") from err
