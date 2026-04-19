"""Yandex Music OAuth Device Flow authentication.

Alternative entry point to QR auth: the user opens a verification URL on any
device, types a short code shown by Music Assistant, and the provider polls
Yandex Passport until the user confirms. Returns the full credential triple
(x_token, music_token, refresh_token) thanks to ``ya-passport-auth`` v1.3.0,
which uses the same Passport Android ``client_id`` as the QR flow.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from music_assistant_models.errors import LoginFailed
from ya_passport_auth import PassportClient
from ya_passport_auth.exceptions import DeviceCodeTimeoutError, YaPassportError

from music_assistant.helpers.auth import AuthenticationHelper

if TYPE_CHECKING:
    from music_assistant import MusicAssistant

_LOGGER = logging.getLogger(__name__)


async def perform_device_auth(mass: MusicAssistant, session_id: str) -> tuple[str, str, str]:
    """Perform Yandex OAuth Device Flow and return credential tokens.

    Asks Yandex for a device code, presents the verification URL and user
    code in the MA frontend, then polls until the user confirms or the code
    expires.

    Returns (x_token, music_token, refresh_token) as plain strings for MA
    config storage.
    """
    try:
        async with PassportClient.create() as client:
            session = await client.start_device_login()

            # AuthenticationHelper can only open one URL — append the user
            # code as a query param so the verification page can pre-fill
            # it (and so the user can read it from the address bar).
            url = f"{session.verification_url}?user_code={session.user_code}"
            _LOGGER.info(
                "Device flow started: open %s and enter code %s (expires in %ss)",
                session.verification_url,
                session.user_code,
                session.expires_in,
            )

            async with AuthenticationHelper(mass, session_id) as auth_helper:
                auth_helper.send_url(url)
                creds = await client.poll_device_until_confirmed(session)

            music_token = creds.music_token
            if music_token is None:
                raise LoginFailed("Device auth succeeded but no music token was returned")
            refresh_token = creds.refresh_token
            if refresh_token is None:
                raise LoginFailed("Device auth succeeded but no refresh token was returned")

            _LOGGER.debug("Device flow complete, obtained full credential triple")
            return (
                creds.x_token.get_secret(),
                music_token.get_secret(),
                refresh_token.get_secret(),
            )

    except DeviceCodeTimeoutError as err:
        raise LoginFailed("Device authentication timed out. Please try again.") from err
    except YaPassportError as err:
        raise LoginFailed(f"Yandex device auth error: {err}") from err
