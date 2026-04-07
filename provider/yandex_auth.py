"""Yandex Passport QR authentication flow.

Adapted from AlexxIT/YandexStation (MIT license) and
trudenboy/ma-provider-yandex-station session.py.
Stripped to authentication-only; uses pure aiohttp.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING

import aiohttp
from music_assistant_models.errors import LoginFailed

from music_assistant.helpers.auth import AuthenticationHelper

if TYPE_CHECKING:
    from music_assistant import MusicAssistant

_LOGGER = logging.getLogger(__name__)

# Yandex Passport OAuth credentials (public, from Yandex Music Android app)
PASSPORT_CLIENT_ID = "c0ebe342af7d48fbbbfcf2d2eedb8f9e"
PASSPORT_CLIENT_SECRET = "ad0a908f0aa341a182a37ecd75bc319e"

# Yandex Music OAuth credentials (from yandex-music-api)
MUSIC_CLIENT_ID = "23cabbbdc6cd418abb4b39c32c41195d"
MUSIC_CLIENT_SECRET = "53bc75238f0c4d08a118e51fe9203300"

# Endpoints
PASSPORT_URL = "https://passport.yandex.ru"
PASSPORT_API_URL = "https://mobileproxy.passport.yandex.net"
MUSIC_TOKEN_URL = "https://oauth.mobile.yandex.net/1/token"

# Polling settings
QR_POLL_INTERVAL = 2.0  # seconds between status checks
QR_POLL_TIMEOUT = 120.0  # total seconds to wait for QR scan


class YandexQRAuth:
    """Yandex Passport QR authentication.

    Uses a dedicated aiohttp session with its own cookie jar
    to avoid leaking Yandex cookies into the shared MA session.
    """

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize with a dedicated aiohttp session."""
        self._session = session

    async def get_qr(self) -> tuple[str, str, str]:
        """Start QR code auth session.

        Returns (qr_url, csrf_token, track_id).
        Raises LoginFailed on any error.
        """
        # Step 1: Get CSRF token from passport page
        async with self._session.get(f"{PASSPORT_URL}/am?app_platform=android") as resp:
            html = await resp.text()
            match = re.search(r'"csrf_token"\s*value="([^"]+)"', html)
            if not match:
                raise LoginFailed("Failed to obtain CSRF token from Yandex Passport")

        csrf_token = match[1]

        # Step 2: Create QR auth session
        async with self._session.post(
            f"{PASSPORT_URL}/registration-validations/auth/password/submit",
            data={
                "csrf_token": csrf_token,
                "retpath": "https://passport.yandex.ru/profile",
                "with_code": 1,
            },
        ) as resp:
            data = await resp.json()

        if data.get("status") != "ok":
            raise LoginFailed("Failed to create QR auth session")

        track_id = data["track_id"]
        csrf_token = data.get("csrf_token", csrf_token)
        qr_url = f"{PASSPORT_URL}/auth/magic/code/?track_id={track_id}"

        _LOGGER.debug("QR auth session created, track_id=%s", track_id)
        return qr_url, csrf_token, track_id

    async def check_qr_status(self, csrf_token: str, track_id: str) -> bool:
        """Check if QR code was scanned and approved.

        Returns True if approved, False if still pending.
        """
        async with self._session.post(
            f"{PASSPORT_URL}/auth/new/magic/status/",
            data={"csrf_token": csrf_token, "track_id": track_id},
        ) as resp:
            data = await resp.json()

        return bool(data.get("status") == "ok")

    async def get_x_token(self) -> str:
        """Exchange session cookies for x_token.

        Must be called after successful QR auth (cookies are in the session jar).
        """
        cookies = "; ".join(
            f"{c.key}={c.value}"
            for c in self._session.cookie_jar
            if c["domain"].endswith("yandex.ru")
        )

        async with self._session.post(
            f"{PASSPORT_API_URL}/1/bundle/oauth/token_by_sessionid",
            data={
                "client_id": PASSPORT_CLIENT_ID,
                "client_secret": PASSPORT_CLIENT_SECRET,
            },
            headers={
                "Ya-Client-Host": "passport.yandex.ru",
                "Ya-Client-Cookie": cookies,
            },
        ) as resp:
            data = await resp.json()

        if "access_token" not in data:
            raise LoginFailed("Failed to exchange session for x_token")

        return str(data["access_token"])

    async def get_music_token(self, x_token: str) -> str:
        """Exchange x_token for a music-scoped OAuth token.

        Can be called standalone (no prior QR flow needed) for token refresh.
        """
        async with self._session.post(
            MUSIC_TOKEN_URL,
            data={
                "client_id": MUSIC_CLIENT_ID,
                "client_secret": MUSIC_CLIENT_SECRET,
                "grant_type": "x-token",
                "access_token": x_token,
            },
        ) as resp:
            data = await resp.json()

        if "access_token" not in data:
            raise LoginFailed("Failed to obtain music token from x_token")

        return str(data["access_token"])


async def perform_qr_auth(mass: MusicAssistant, session_id: str) -> tuple[str, str]:
    """Perform full QR authentication flow.

    Opens a QR code popup via MA frontend, polls for scan confirmation,
    then exchanges for x_token and music_token.

    Returns (x_token, music_token).
    """
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        auth = YandexQRAuth(session)

        # Get QR code URL
        qr_url, csrf_token, track_id = await auth.get_qr()

        # Open QR page in MA frontend popup
        async with AuthenticationHelper(mass, session_id) as auth_helper:
            auth_helper.send_url(qr_url)

            # Poll for QR scan confirmation
            elapsed = 0.0
            while elapsed < QR_POLL_TIMEOUT:
                await asyncio.sleep(QR_POLL_INTERVAL)
                elapsed += QR_POLL_INTERVAL

                if await auth.check_qr_status(csrf_token, track_id):
                    _LOGGER.debug("QR code confirmed after %.0fs", elapsed)
                    break
            else:
                raise LoginFailed("QR authentication timed out. Please try again.")

        # Exchange cookies → x_token → music_token
        x_token = await auth.get_x_token()
        music_token = await auth.get_music_token(x_token)

        _LOGGER.debug("QR auth complete, obtained both tokens")
        return x_token, music_token


async def refresh_music_token(x_token: str) -> str:
    """Refresh music token from a stored x_token.

    Creates a throwaway HTTP session for the single API call.
    """
    async with aiohttp.ClientSession() as session:
        auth = YandexQRAuth(session)
        return await auth.get_music_token(x_token)
