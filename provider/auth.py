"""Yandex Music authentication flows.

Two user-facing login paths, both backed by ``ya-passport-auth``:

* **QR flow** — :func:`perform_qr_auth` opens a QR popup via the MA frontend
  and polls Passport until the user scans/confirms. Yields
  ``(x_token, music_token)``.
* **Device Flow** — :func:`perform_device_auth` serves a short user code on
  an MA-hosted intermediate page and polls Passport until confirmation.
  Yields the full ``(x_token, music_token, refresh_token)`` triple thanks
  to ``ya-passport-auth`` v1.3.0 reusing the same Passport Android
  ``client_id`` as the QR flow.

Token maintenance helpers (:func:`refresh_music_token`,
:func:`refresh_credentials_via_passport`, :func:`validate_x_token`) live
alongside the login flows.
"""

from __future__ import annotations

import asyncio
import html
import json
import logging
import time
from string import Template
from typing import TYPE_CHECKING, Final

from aiohttp import web
from music_assistant_models.errors import LoginFailed, ResourceTemporarilyUnavailable
from ya_passport_auth import Credentials, PassportClient, SecretStr
from ya_passport_auth.exceptions import (
    DeviceCodeTimeoutError,
    InvalidCredentialsError,
    NetworkError,
    QRTimeoutError,
    RateLimitedError,
    YaPassportError,
)

from music_assistant.helpers.auth import AuthenticationHelper

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from typing import Any

    from ya_passport_auth import DeviceCodeSession

    from music_assistant import MusicAssistant

_LOGGER = logging.getLogger(__name__)

_DEVICE_CODE_PAGE_PATH = "/yandex_music/device_code"
# Seconds to keep the status endpoint alive after the flow finishes so the
# intermediate page has a chance to poll once more and close itself. The wait
# runs in a background task — it never delays the config flow's response.
_POST_AUTH_GRACE_SECONDS = 3

# Pending deferred route teardowns keyed by page path, so a rapid retry with
# the same session id can take the routes over instead of colliding.
_pending_teardowns: dict[str, asyncio.Task[None]] = {}

# JS-consumed subset of the page strings; the rest is substituted server-side.
_JS_STRING_KEYS: Final = (
    "copied",
    "copy_manual",
    "hint_copy",
    "expired_title",
    "expired_text",
    "success_title",
    "success_text",
    "failed_title",
    "failed_text",
    "denied_text",
    "ended_title",
    "ended_text",
)

_PAGE_STRINGS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "lang": "en",
        "title": "Login to Yandex Music",
        "step_copy": "Copy the code",
        "hint_copy": "Tap the code to copy it",
        "copied": "Copied ✓",
        "copy_manual": "Automatic copy failed — select the code and copy it manually",
        "step_open": "Open the Yandex page and enter the code",
        "open_button": "Continue to Yandex",
        "expires_label": "Code expires in",
        "expired_title": "Code expired",
        "expired_text": (
            "The code is no longer valid. Return to Music Assistant and start the login again."
        ),
        "success_title": "Authorization successful",
        "success_text": "You can close this window.",
        "failed_title": "Authorization failed",
        "failed_text": "Please return to Music Assistant and try again.",
        "denied_text": "The login was denied. Return to Music Assistant and try again.",
        "ended_title": "Session ended",
        "ended_text": "This login session is no longer active. You can close this window.",
    },
    "ru": {
        "lang": "ru",
        "title": "Вход в Яндекс Музыку",
        "step_copy": "Скопируйте код",
        "hint_copy": "Нажмите на код, чтобы скопировать",
        "copied": "Скопировано ✓",
        "copy_manual": "Не удалось скопировать автоматически — выделите код и скопируйте вручную",  # noqa: RUF001
        "step_open": "Откройте страницу Яндекса и введите код",
        "open_button": "Перейти на Яндекс",
        "expires_label": "Код истекает через",
        "expired_title": "Код истёк",
        "expired_text": (
            "Код больше не действует. Вернитесь в Music Assistant и начните вход заново."
        ),
        "success_title": "Авторизация выполнена",
        "success_text": "Это окно можно закрыть.",
        "failed_title": "Авторизация не удалась",
        "failed_text": "Вернитесь в Music Assistant и попробуйте ещё раз.",
        "denied_text": "Вход был отклонён. Вернитесь в Music Assistant и попробуйте ещё раз.",
        "ended_title": "Сессия завершена",
        "ended_text": "Эта сессия входа больше не активна. Это окно можно закрыть.",
    },
}


_PAGE_TEMPLATE: Final = Template("""<!DOCTYPE html>
<html lang="$lang">
<head>
    <meta charset="utf-8">
    <title>$title</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root { color-scheme: light dark; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0; padding: 2rem 1rem;
            display: flex; align-items: center; justify-content: center;
            min-height: 100vh; box-sizing: border-box;
            background: #f5f5f7; color: #1d1d1f;
        }
        .card {
            background: #ffffff;
            border-radius: 14px; padding: 2rem;
            max-width: 28rem; width: 100%;
            box-shadow: 0 4px 20px rgba(0,0,0,.08);
            text-align: center;
        }
        h1 { margin: 0 0 1rem; font-size: 1.25rem; }
        .steps { margin: 0; padding: 0 0 0 1.4rem; text-align: left; }
        .steps li { margin: 0 0 1.25rem; }
        .steps li:last-child { margin-bottom: 0; }
        .step-label { display: block; margin-bottom: .5rem; line-height: 1.45; }
        #code {
            display: inline-block;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 2rem; font-weight: 600; letter-spacing: .15em;
            padding: .75rem 1.25rem; border-radius: 10px;
            background: #f2f2f7;
            border: 1px dashed #c8c8cd;
            cursor: pointer;
            user-select: all;
        }
        #code.copied { background: #d9f2dd; border-color: #34c759; }
        .hint { margin-top: .4rem; font-size: .85rem; color: #6e6e73; }
        .url {
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: .95rem; word-break: break-all;
            margin-bottom: .5rem;
        }
        .btn {
            display: inline-block; padding: .6rem 1.25rem;
            font-size: 1rem; font-weight: 600; text-decoration: none;
            border-radius: 10px;
            background: #ffcc00; color: #1d1d1f;
        }
        .btn:hover { background: #ffd633; }
        #timer { margin-top: 1.25rem; }
        p { margin: .5rem 0 0; color: #6e6e73; line-height: 1.45; }
        @media (prefers-color-scheme: dark) {
            body { background: #1c1c1e; color: #f2f2f7; }
            .card { background: #2c2c2e; box-shadow: 0 4px 20px rgba(0,0,0,.4); }
            #code { background: #3a3a3c; border-color: #545456; }
            #code.copied { background: #1f4526; border-color: #30d158; }
            .hint, p { color: #98989e; }
        }
    </style>
</head>
<body>
    <div class="card" id="card">
        <h1>$title</h1>
        <ol class="steps">
            <li>
                <span class="step-label">$step_copy</span>
                <div id="code" role="button" tabindex="0">$user_code</div>
                <div id="copy-hint" class="hint">$hint_copy</div>
            </li>
            <li>
                <span class="step-label">$step_open</span>
                <div class="url">$verification_url</div>
                <a class="btn" href="$verification_url" target="_blank"
                   rel="noopener">$open_button</a>
            </li>
        </ol>
        <div id="timer" class="hint">$expires_label <span id="countdown"></span></div>
    </div>
    <script>
        const statusUrl = $status_url_js;
        const strings = $strings_js;
        let remaining = $expires_in;
        let terminal = false;

        const card = document.getElementById('card');
        const codeElement = document.getElementById('code');
        const hintElement = document.getElementById('copy-hint');
        const countdownElement = document.getElementById('countdown');

        function showResult(title, message) {
            terminal = true;
            card.innerHTML = '<h1>' + title + '</h1><p>' + message + '</p>';
        }

        function fallbackCopy() {
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(codeElement);
            selection.removeAllRanges();
            selection.addRange(range);
            let ok = false;
            try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
            return ok;
        }

        async function copyCode() {
            const code = codeElement.textContent.trim();
            let ok = false;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                try {
                    await navigator.clipboard.writeText(code);
                    ok = true;
                } catch (e) { ok = false; }
            }
            if (!ok) ok = fallbackCopy();
            codeElement.classList.toggle('copied', ok);
            if (hintElement) {
                hintElement.textContent = ok ? strings.copied : strings.copy_manual;
            }
            if (ok) {
                setTimeout(() => {
                    codeElement.classList.remove('copied');
                    if (hintElement) hintElement.textContent = strings.hint_copy;
                }, 2000);
            }
        }
        if (codeElement) {
            codeElement.addEventListener('click', copyCode);
            codeElement.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); copyCode(); }
            });
        }

        function renderCountdown() {
            if (!countdownElement) return;
            const m = Math.floor(remaining / 60);
            const s = String(remaining % 60).padStart(2, '0');
            countdownElement.textContent = m + ':' + s;
        }
        renderCountdown();
        const timerId = setInterval(() => {
            remaining -= 1;
            if (terminal) { clearInterval(timerId); return; }
            if (remaining <= 0) {
                clearInterval(timerId);
                showResult(strings.expired_title, strings.expired_text);
                return;
            }
            renderCountdown();
        }, 1000);

        async function pollStatus() {
            if (terminal) return;
            try {
                const r = await fetch(statusUrl, { cache: 'no-store' });
                if (r.status === 404 || r.status === 410) {
                    showResult(strings.ended_title, strings.ended_text);
                    return;
                }
                if (r.ok) {
                    const data = await r.json();
                    if (data.state === 'done') {
                        showResult(strings.success_title, strings.success_text);
                        setTimeout(() => { try { window.close(); } catch (e) {} }, 300);
                        return;
                    }
                    if (data.state === 'failed') {
                        if (data.reason === 'expired') {
                            showResult(strings.expired_title, strings.expired_text);
                        } else if (data.reason === 'denied') {
                            showResult(strings.failed_title, strings.denied_text);
                        } else {
                            showResult(strings.failed_title, strings.failed_text);
                        }
                        return;
                    }
                }
            } catch (e) { /* network hiccup — retry */ }
            setTimeout(pollStatus, 2000);
        }
        setTimeout(pollStatus, 2000);
    </script>
</body>
</html>
""")


def _resolve_language(mass: MusicAssistant) -> str:
    """Return the page language ("ru" or "en") for the active MA locale."""
    if isinstance(locale := _safe_locale(mass), str) and locale.lower().startswith("ru"):
        return "ru"
    return "en"


def _safe_locale(mass: MusicAssistant) -> str | None:
    """Return the active MA locale string, or None when unavailable."""
    try:
        locale = mass.metadata.locale
    except Exception:
        return None
    return locale if isinstance(locale, str) else None


async def _resolve_page_strings(mass: MusicAssistant) -> dict[str, str]:
    """
    Resolve the device-code page strings for the active MA locale.

    Prefers the MA translations catalog (strings.json → Lokalise) and falls
    back per key to the in-code English/Russian table when a translation is
    not yet available or the MA build predates the translations controller.
    """
    fallback = dict(_PAGE_STRINGS[_resolve_language(mass)])
    translations = getattr(mass, "translations", None)
    if translations is None:
        return fallback
    locale = _safe_locale(mass)
    try:
        await translations.ensure_locale_loaded(locale)
    except Exception as err:
        _LOGGER.debug("Could not load locale catalog %s: %s", locale, err)
        return fallback
    for key in fallback:
        if key == "lang":
            continue
        try:
            value = translations.get_translation(
                f"page.device_code.{key}", locale=locale, owner="yandex_music"
            )
        except Exception as err:
            _LOGGER.debug("Translation lookup failed for %s: %s", key, err)
            return fallback
        if isinstance(value, str):
            fallback[key] = value
    return fallback


def _make_route_handlers(
    session: DeviceCodeSession,
    status_url: str,
    state: dict[str, str],
    strings: dict[str, str],
) -> tuple[
    Callable[[web.Request], Coroutine[Any, Any, web.Response]],
    Callable[[web.Request], Coroutine[Any, Any, web.Response]],
]:
    """
    Build the (page, status) request handlers for a device-code login session.

    :param session: The device-code session issued by Yandex.
    :param status_url: MA-hosted endpoint the page polls for the login state.
    :param state: Mutable login state shared with the flow; served as JSON.
    :param strings: Resolved page strings (see :func:`_resolve_page_strings`).
    """
    issued_at = time.monotonic()

    async def _serve_page(_request: web.Request) -> web.Response:
        # Render per request so the countdown reflects the time the code has
        # actually left (late popup open, page reload).
        remaining = max(0, session.expires_in - int(time.monotonic() - issued_at))
        return web.Response(
            text=_build_device_code_page(
                user_code=session.user_code,
                verification_url=session.verification_url,
                status_url=status_url,
                expires_in=remaining,
                strings=strings,
            ),
            content_type="text/html",
            charset="utf-8",
            headers={
                "Cache-Control": "no-store",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    async def _serve_status(_request: web.Request) -> web.Response:
        return web.json_response(
            dict(state),
            headers={"Cache-Control": "no-store"},
        )

    return _serve_page, _serve_status


def _cancel_pending_teardown(page_path: str) -> None:
    """Cancel a pending route teardown left by a previous login attempt.

    :param page_path: Page route path whose deferred teardown should be
        cancelled before the routes are taken over by a new attempt.
    """
    task = _pending_teardowns.pop(page_path, None)
    if task is not None:
        task.cancel()


def _schedule_route_teardown(mass: MusicAssistant, page_path: str, status_path: str) -> None:
    """Unregister the login page routes after the grace period, without blocking.

    :param mass: The MusicAssistant instance owning the webserver routes.
    :param page_path: Page route path (GET) to unregister.
    :param status_path: Status route path (GET) to unregister.
    """

    async def _teardown() -> None:
        await asyncio.sleep(_POST_AUTH_GRACE_SECONDS)
        for path in (page_path, status_path):
            # The webserver may already be shutting down — one failed
            # unregister must not skip the remaining route.
            try:
                mass.webserver.unregister_dynamic_route(path, "GET")
            except Exception as err:
                _LOGGER.debug("Could not unregister route %s: %s", path, err)

    task = mass.create_task(_teardown())
    _pending_teardowns[page_path] = task

    def _discard(done: asyncio.Task[None]) -> None:
        if _pending_teardowns.get(page_path) is done:
            del _pending_teardowns[page_path]

    task.add_done_callback(_discard)


def _build_device_code_page(
    *,
    user_code: str,
    verification_url: str,
    status_url: str,
    expires_in: int,
    strings: dict[str, str],
) -> str:
    """
    Render the HTML page shown to the user during Device Flow login.

    Yandex's verification page does not pre-fill the code from query params,
    and the MA frontend opens auth URLs in a new tab, so the user would
    otherwise have no signal that authorization succeeded. The page polls the
    status endpoint and closes itself (or shows a terminal message) when the
    backend signals completion.

    :param user_code: Short confirmation code the user enters on Yandex.
    :param verification_url: Yandex page where the code must be entered.
    :param status_url: MA-hosted endpoint the page polls for the login state.
    :param expires_in: Code lifetime in seconds; drives the on-page countdown.
    :param strings: Resolved page strings (see :func:`_resolve_page_strings`).
    """
    # json.dumps emits a JS string literal, but `</script>` would still break
    # out of the surrounding <script> block. Escape the slash to be safe.
    safe_status_url = json.dumps(status_url).replace("</", "<\\/")
    js_strings = {key: strings[key] for key in _JS_STRING_KEYS}
    safe_strings = json.dumps(js_strings, ensure_ascii=False).replace("</", "<\\/")
    return _PAGE_TEMPLATE.substitute(
        lang=strings["lang"],
        title=html.escape(strings["title"]),
        step_copy=html.escape(strings["step_copy"]),
        hint_copy=html.escape(strings["hint_copy"]),
        step_open=html.escape(strings["step_open"]),
        open_button=html.escape(strings["open_button"]),
        expires_label=html.escape(strings["expires_label"]),
        user_code=html.escape(user_code),
        verification_url=html.escape(verification_url, quote=True),
        status_url_js=safe_status_url,
        strings_js=safe_strings,
        expires_in=str(int(expires_in)),
    )


async def perform_device_auth(mass: MusicAssistant, session_id: str) -> tuple[str, str, str]:
    """Perform Yandex OAuth Device Flow and return credential tokens.

    Asks Yandex for a device code, presents it to the user via an intermediate
    HTML page served from MA's own webserver, then polls until the user
    confirms or the code expires. Returns (or raises) as soon as the outcome
    is known.

    Returns (x_token, music_token, refresh_token) as plain strings for MA
    config storage.
    """
    try:
        async with PassportClient.create() as client:
            session = await client.start_device_login()

            _LOGGER.info(
                "Device flow started: open %s (expires in %ss)",
                session.verification_url,
                session.expires_in,
            )
            _LOGGER.debug("Device flow user_code issued")

            page_path = f"{_DEVICE_CODE_PAGE_PATH}/{session_id}"
            status_path = f"{page_path}/status"
            status_url = f"{mass.webserver.base_url}{status_path}"
            state: dict[str, str] = {"state": "pending"}
            serve_page, serve_status = _make_route_handlers(
                session, status_url, state, await _resolve_page_strings(mass)
            )

            try:
                # A rapid retry can reuse the session id while the previous
                # attempt's routes still await their grace-period teardown —
                # take the paths over instead of colliding.
                _cancel_pending_teardown(page_path)
                mass.webserver.unregister_dynamic_route(page_path, "GET")
                mass.webserver.unregister_dynamic_route(status_path, "GET")
                mass.webserver.register_dynamic_route(page_path, serve_page, "GET")
                mass.webserver.register_dynamic_route(status_path, serve_status, "GET")
                async with AuthenticationHelper(mass, session_id) as auth_helper:
                    auth_helper.send_url(f"{mass.webserver.base_url}{page_path}")
                    try:
                        creds = await client.poll_device_until_confirmed(session)
                    except asyncio.CancelledError:
                        # Don't mark cancellations as auth failures.
                        raise
                    except Exception as exc:
                        reason = (
                            "expired"
                            if isinstance(exc, DeviceCodeTimeoutError)
                            else "denied"
                            if isinstance(exc, InvalidCredentialsError)
                            else "error"
                        )
                        state.update({"state": "failed", "reason": reason})
                        raise

                    music_token = creds.music_token
                    refresh_token = creds.refresh_token
                    if music_token is None or refresh_token is None:
                        state.update({"state": "failed", "reason": "error"})
                        missing = "music" if music_token is None else "refresh"
                        raise LoginFailed(
                            f"Device auth succeeded but no {missing} token was returned"
                        )
                    state["state"] = "done"
            finally:
                # The page needs one more poll to observe the terminal state —
                # keep the routes alive for the grace period in the background
                # instead of delaying the config flow's response.
                _schedule_route_teardown(mass, page_path, status_path)

            _LOGGER.debug("Device flow complete, obtained full credential triple")
            return (
                creds.x_token.get_secret(),
                music_token.get_secret(),
                refresh_token.get_secret(),
            )

    except DeviceCodeTimeoutError as err:
        raise LoginFailed("Device authentication timed out. Please try again.") from err
    except InvalidCredentialsError as err:
        raise LoginFailed("Device authentication was denied. Please try again.") from err
    except YaPassportError as err:
        raise LoginFailed(f"Yandex device auth error ({type(err).__name__})") from err


async def perform_qr_auth(mass: MusicAssistant, session_id: str) -> tuple[str, str]:
    """Perform full QR authentication flow.

    Opens a QR code popup via MA frontend, polls for scan confirmation,
    then returns tokens as plain strings for MA config storage.

    Returns (x_token, music_token).
    """
    try:
        async with PassportClient.create() as client:
            qr = await client.start_qr_login()

            async with AuthenticationHelper(mass, session_id) as auth_helper:
                auth_helper.send_url(qr.qr_url)
                creds = await client.poll_qr_until_confirmed(qr)

            x_token = creds.x_token.get_secret()
            music_token = creds.music_token
            if music_token is None:
                raise LoginFailed("QR auth succeeded but no music token was returned")

            _LOGGER.debug("QR auth complete, obtained both tokens")
            return x_token, music_token.get_secret()

    except QRTimeoutError as err:
        raise LoginFailed("QR authentication timed out. Please try again.") from err
    except YaPassportError as err:
        raise LoginFailed(f"Yandex auth error ({type(err).__name__})") from err


async def refresh_music_token(x_token: SecretStr) -> SecretStr:
    """Exchange an x_token for a fresh music-scoped OAuth token.

    Distinguishes transient Passport failures (network/rate limiting) from
    credential-invalid errors: only the latter raise ``LoginFailed``, so
    callers don't clear stored tokens on a Passport blip.
    """
    try:
        async with PassportClient.create() as client:
            return await client.refresh_music_token(x_token)
    except (NetworkError, RateLimitedError) as err:
        # Library exception strings may carry request bodies or token fragments;
        # surface only the class name to keep MA logs and the frontend clean.
        raise ResourceTemporarilyUnavailable(
            f"Yandex Passport temporarily unavailable ({type(err).__name__})"
        ) from err
    except YaPassportError as err:
        raise LoginFailed(f"Failed to refresh music token ({type(err).__name__})") from err


async def refresh_credentials_via_passport(
    x_token: SecretStr, refresh_token: SecretStr
) -> Credentials:
    """Silently re-issue the full credential triple using a refresh token.

    Only available for accounts authenticated via the Device Flow (QR login
    does not yield a ``refresh_token``). Rotates both ``x_token`` and
    ``refresh_token`` server-side, so callers must persist the returned
    Credentials.
    """
    try:
        async with PassportClient.create() as client:
            return await client.refresh_credentials(
                Credentials(x_token=x_token, refresh_token=refresh_token)
            )
    except (NetworkError, RateLimitedError) as err:
        raise ResourceTemporarilyUnavailable(
            f"Yandex Passport temporarily unavailable ({type(err).__name__})"
        ) from err
    except YaPassportError as err:
        raise LoginFailed(f"Failed to refresh credentials ({type(err).__name__})") from err


async def validate_x_token(x_token: SecretStr) -> bool:
    """Return True if *x_token* is still accepted by Yandex Passport.

    A ``False`` return signals "rejected by Passport" — a terminal credential
    failure. Transient network or rate-limit errors are re-raised so callers
    can distinguish them from invalid credentials and avoid clearing a good
    token on a temporary outage.

    :raises NetworkError: Transient network failure reaching Passport.
    :raises RateLimitedError: Passport returned 429.
    """
    try:
        async with PassportClient.create() as client:
            return bool(await client.validate_x_token(x_token))
    except NetworkError, RateLimitedError:
        raise
    except YaPassportError:
        return False
