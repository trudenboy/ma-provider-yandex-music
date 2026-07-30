# Manual Token Authentication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add manual-token setup, safe advanced token replacement, and clear reconfigure behavior without changing QR as the default.

**Architecture:** The setup flow accepts a conditional secure token in the same method-selection form and persists it through Music Assistant's encrypted setup data. Advanced replacement uses a separate one-shot secure option: provider initialization validates it before promoting it into setup data and removing the old session credentials. Music Assistant's existing provider `Reconfigure` command remains the forced reauthentication entry point.

**Tech Stack:** Python 3.12+, Music Assistant setup/config APIs, `music_assistant_models`, pytest, Docker, Ruff.

## Global Constraints

- QR remains the default setup method.
- Secrets are never returned to the frontend or retained in the one-shot advanced option after validation.
- A failed replacement must not overwrite existing setup credentials.
- A successful manual replacement clears `x_token` and `refresh_token`.
- No Music Assistant frontend change is included.

---

### Task 1: Manual token setup method

**Files:**
- Modify: `tests/test_setup_flow.py`
- Modify: `provider/setup_flow.py`

**Interfaces:**
- Produces: `METHOD_TOKEN = "token"` and the existing `run_setup(session)` accepting `CONF_TOKEN` when that method is selected.
- Persists: `{CONF_TOKEN: token, CONF_X_TOKEN: None, CONF_REFRESH_TOKEN: None}`.

- [ ] **Step 1: Write failing setup-flow tests**

Add tests that inspect the first form and require:

```python
token_entry = next(entry for entry in form.entries if entry.key == CONF_TOKEN)
remember_entry = next(entry for entry in form.entries if entry.key == CONF_REMEMBER_SESSION)
assert token_entry.type == ConfigEntryType.SECURE_STRING
assert token_entry.depends_on == ym_flow.CONF_METHOD
assert token_entry.depends_on_value == ym_flow.METHOD_TOKEN
assert remember_entry.depends_on_value_not == ym_flow.METHOD_TOKEN
```

Drive `run_setup` with `{CONF_METHOD: METHOD_TOKEN, CONF_TOKEN: "manual-token"}` and assert that `session.finish` receives the manual token and clears both long-lived session credentials. Add a missing-token case that re-renders the form with `errors[CONF_TOKEN] == "required"` without calling Passport.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
docker exec ma-yandex-functional-v385 pytest -q /app/tests/test_setup_flow.py
```

Expected: failure because `METHOD_TOKEN` and the conditional secure field do not exist.

- [ ] **Step 3: Implement the setup method**

In `provider/setup_flow.py`, add `METHOD_TOKEN`, add an optional conditional `SECURE_STRING` `CONF_TOKEN` entry, and make `CONF_REMEMBER_SESSION` depend on method not being `METHOD_TOKEN`. Branch before Passport login:

```python
if method == METHOD_TOKEN:
    token = values.get(CONF_TOKEN)
    if not token:
        errors = {CONF_TOKEN: "required"}
        continue
    collected = {CONF_TOKEN: str(token), CONF_X_TOKEN: None, CONF_REFRESH_TOKEN: None}
else:
    # existing QR/device credential collection
```

Keep `session.finish` inside the existing retry loop so provider validation errors return to the form.

- [ ] **Step 4: Run setup-flow tests and verify GREEN**

Run the Task 1 command. Expected: all `tests/test_setup_flow.py` tests pass.

- [ ] **Step 5: Commit Task 1**

```bash
git add provider/setup_flow.py tests/test_setup_flow.py
git commit -m "feat: add manual token setup method"
```

### Task 2: Advanced replacement-token option

**Files:**
- Modify: `provider/constants.py`
- Modify: `provider/provider.py`
- Modify: `tests/test_config_entries.py`

**Interfaces:**
- Produces: `CONF_MANUAL_TOKEN = "manual_token"`.
- Config entry: optional `ConfigEntryType.SECURE_STRING`, `advanced=True`, `requires_reload=True`.

- [ ] **Step 1: Write a failing config-entry test**

Replace the no-auth-entry assertion with a focused test requiring the one-shot replacement entry while continuing to reject old auth actions:

```python
entry = next(e for e in entries if e.key == CONF_MANUAL_TOKEN)
assert entry.type == ConfigEntryType.SECURE_STRING
assert entry.required is False
assert entry.advanced is True
assert entry.requires_reload is True
assert {e.action for e in entries if e.action}.isdisjoint(
    {"auth_device", "auth_qr", "clear_auth"}
)
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
docker exec ma-yandex-functional-v385 pytest -q /app/tests/test_config_entries.py
```

Expected: failure because `CONF_MANUAL_TOKEN` and its entry do not exist.

- [ ] **Step 3: Add the advanced secure entry**

Declare `CONF_MANUAL_TOKEN` in `provider/constants.py`, import it in `provider/provider.py`, and append the secure advanced entry to `get_config_entries`. It is optional and requests a provider reload when changed.

- [ ] **Step 4: Run config-entry tests and verify GREEN**

Run the Task 2 command. Expected: all `tests/test_config_entries.py` tests pass.

- [ ] **Step 5: Commit Task 2**

```bash
git add provider/constants.py provider/provider.py tests/test_config_entries.py
git commit -m "feat: expose advanced token replacement"
```

### Task 3: Validate and promote replacement token

**Files:**
- Modify: `provider/provider.py`
- Modify: `tests/test_provider.py`

**Interfaces:**
- Consumes: `CONF_MANUAL_TOKEN` from Task 2.
- Changes: `handle_async_init()` gives a non-empty one-shot token priority over stored setup credentials.
- Side effects after successful validation: update setup `CONF_TOKEN`, clear setup `CONF_X_TOKEN` and `CONF_REFRESH_TOKEN`, clear config `CONF_MANUAL_TOKEN` immediately.

- [ ] **Step 1: Write failing provider-auth tests**

Add a successful replacement test where `get_config_value(CONF_MANUAL_TOKEN)` returns `"new-token"`, client connection succeeds, and assertions require:

```python
provider._update_setup_data.assert_any_call(CONF_TOKEN, "new-token")
provider._update_setup_data.assert_any_call(CONF_X_TOKEN, None)
provider._update_setup_data.assert_any_call(CONF_REFRESH_TOKEN, None)
provider._update_config_value.assert_called_with(CONF_MANUAL_TOKEN, None, immediate=True)
```

Add an invalid replacement test where connection raises `LoginFailed`; assert that the temporary option is cleared, no setup-data write occurs, and the error is re-raised. Existing stored tokens must not be attempted in the same initialization.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
docker exec ma-yandex-functional-v385 pytest -q /app/tests/test_provider.py
```

Expected: failure because initialization ignores `CONF_MANUAL_TOKEN`.

- [ ] **Step 3: Implement validation-first promotion**

At the beginning of `handle_async_init`, read the one-shot token. If present, create/connect the normal Yandex client using that token. On `LoginFailed`, clear only `CONF_MANUAL_TOKEN` and re-raise. On success, promote the token and clear old session credentials plus the one-shot option. Continue normal post-connect initialization without reconnecting or falling back to old credentials.

- [ ] **Step 4: Run auth and related tests and verify GREEN**

Run:

```bash
docker exec ma-yandex-functional-v385 pytest -q /app/tests/test_provider.py /app/tests/test_config_entries.py /app/tests/test_setup_flow.py
```

Expected: all selected tests pass.

- [ ] **Step 5: Commit Task 3**

```bash
git add provider/provider.py tests/test_provider.py
git commit -m "feat: validate manual token replacements"
```

### Task 4: UI copy, regression suite, and functional Docker

**Files:**
- Modify: `provider/strings.json`
- Modify: `tests/test_localization.py`

**Interfaces:**
- Adds translations for method option `token`, setup token field, and advanced `manual_token` field.
- Documents `Reconfigure` as the supported forced authentication restart.

- [ ] **Step 1: Add a failing strings assertion**

Extend `tests/test_localization.py` with a test that loads `provider/strings.json` and requires method option `token`, `config_entries.token`, and `config_entries.manual_token` text.

- [ ] **Step 2: Run it and verify RED**

Run the focused test file. Expected: failure because translations are absent.

- [ ] **Step 3: Add concise UI text**

Describe manual token setup, explain that it does not auto-refresh, and explain that the advanced field is one-shot and blank keeps the current token. The setup-flow description tells existing users to use the provider's `...` → `Reconfigure` command for a forced login restart.

- [ ] **Step 4: Run focused and full verification**

Run:

```bash
docker exec ma-yandex-functional-v385 pytest -q /app/tests/test_setup_flow.py /app/tests/test_config_entries.py /app/tests/test_provider.py /app/tests/test_localization.py
docker exec ma-yandex-functional-v385 pytest -q /app/tests
docker exec ma-yandex-functional-v385 ruff check /app/music_assistant/providers/yandex_music /app/tests
docker exec ma-yandex-functional-v385 ruff format --check /app/music_assistant/providers/yandex_music /app/tests
```

Expected: all tests pass and Ruff reports no errors or formatting changes.

- [ ] **Step 5: Exercise the functional container**

Restart `ma-yandex-functional-v385` with the worktree mounted, confirm HTTP 200 on port 18095, inspect logs for provider load errors, and manually confirm the setup form exposes QR, Device Code, and Manual token while QR remains selected by default.

- [ ] **Step 6: Self-review and commit Task 4**

Review `git diff --check`, inspect the complete branch diff for leaked secrets, stale translations, or unintended auth behavior, then commit:

```bash
git add provider/strings.json tests/test_localization.py
git commit -m "docs: explain token authentication controls"
```
