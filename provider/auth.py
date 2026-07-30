"""Yandex Music token-maintenance wrappers."""

from __future__ import annotations

from typing import TYPE_CHECKING

# Re-exported as the stable patch target for token-maintenance tests.
from ya_passport_auth import PassportClient  # noqa: F401
from ya_passport_auth.ma import (
    refresh_credentials as _refresh_credentials,
)
from ya_passport_auth.ma import (
    refresh_music_token as _refresh_music_token,
)
from ya_passport_auth.ma import (
    validate_x_token as _validate_x_token,
)

if TYPE_CHECKING:
    from ya_passport_auth import Credentials, SecretStr


async def refresh_music_token(x_token: SecretStr) -> SecretStr:
    """
    Exchange an x_token for a fresh music-scoped OAuth token.

    Distinguishes transient Passport failures (network/rate limiting) from
    credential-invalid errors: only the latter raise ``LoginFailed``, so
    callers don't clear stored tokens on a Passport blip.
    """
    return await _refresh_music_token(x_token)


async def refresh_credentials_via_passport(
    x_token: SecretStr, refresh_token: SecretStr
) -> Credentials:
    """
    Silently re-issue the full credential triple using a refresh token.

    Only available for accounts authenticated via the Device Flow (QR login
    does not yield a ``refresh_token``). Rotates both ``x_token`` and
    ``refresh_token`` server-side, so callers must persist the returned
    Credentials.
    """
    return await _refresh_credentials(x_token, refresh_token)


async def validate_x_token(x_token: SecretStr) -> bool:
    """
    Return True if *x_token* is still accepted by Yandex Passport.

    A ``False`` return signals "rejected by Passport" — a terminal credential
    failure. Transient network or rate-limit errors are re-raised so callers
    can distinguish them from invalid credentials and avoid clearing a good
    token on a temporary outage.

    :raises NetworkError: Transient network failure reaching Passport.
    :raises RateLimitedError: Passport returned 429.
    """
    return await _validate_x_token(x_token)
