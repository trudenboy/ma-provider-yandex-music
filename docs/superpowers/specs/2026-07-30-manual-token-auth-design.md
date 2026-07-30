# Manual token authentication design

## Goal

Extend the existing Yandex Music setup flow with manual token entry, while keeping QR
login as the default. Existing provider instances must also be able to restart the same
authentication flow and replace their token from Advanced settings.

## Setup and reconfigure flow

The login-method selector gains a third `token` option. The secure token field is shown
only while that option is selected; the remember-session switch remains available only
for QR and Device Code. A submitted manual token is passed to `session.finish` as the
music token, while `x_token` and `refresh_token` are cleared. The provider reload performed
by Music Assistant validates the token before the flow succeeds.

QR remains the default method. User-initiated `Reconfigure` uses the same method selector,
so it provides a forced authentication restart even when the provider is healthy.

## Advanced token replacement

Provider options gain an optional advanced `SECURE_STRING` field for a replacement token.
It is a one-shot input and is never populated back into the UI. Saving a non-empty value
reloads the provider and validates that token first. On success, the provider moves it to
encrypted setup data, clears the one-shot field, and removes old session and refresh tokens
so credentials from different accounts cannot be mixed.

An invalid replacement is cleared without overwriting the working setup credentials. The
failed reload reports the authentication error; retrying the provider can therefore return
to the previous credentials, or the user can use `Reconfigure`.

## UI text

Translations identify all three login methods, explain that manual tokens cannot refresh
automatically, and explain that leaving the advanced replacement field empty keeps the
current token. Reconfigure uses the normal Music Assistant provider menu (`...` then
`Reconfigure`); a dedicated button is outside provider control and is not added.

## Tests

Tests cover conditional form metadata, manual setup persistence, setup validation failure,
the advanced secure/reload entry, successful promotion of a replacement token, invalid-token
rollback, and clearing stale session credentials. Existing QR, Device Code, provider, lint,
and full test suites must remain green.
