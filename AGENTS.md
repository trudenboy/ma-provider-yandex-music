<!-- ma-provider-tools: rendered from wrappers/AGENTS.md.j2 -->
# AGENTS.md

The guide for every AI agent working on the **Yandex Music** provider
(Claude Code, Codex, Cursor, Gemini, Copilot and others). It aligns this repo
with the upstream [`music-assistant/server`](https://github.com/music-assistant/server)
standards. `CLAUDE.md` is a symlink to this file, as it is upstream. The file
is rendered from `wrappers/AGENTS.md.j2` in
[`trudenboy/ma-provider-tools`](https://github.com/trudenboy/ma-provider-tools)
and is kept in sync across every provider repo, so **do not edit it here**.

Provider-specific architecture, key flows and gotchas live in
[`CLAUDE.local.md`](./CLAUDE.local.md). Claude Code loads that file
automatically. **Every other agent must read it before changing code.**

## Where the Rules Come From

| Source | Read it |
|---|---|
| This file | always: ecosystem rules plus the upstream MUST list and upstream's own agent guide (at the end) |
| [`CLAUDE.local.md`](./CLAUDE.local.md) | always: this provider's architecture |
| [`.github/instructions/music-assistant-standards.instructions.md`](./.github/instructions/music-assistant-standards.instructions.md) | before writing or reviewing non-trivial provider code: about 60 upstream review precedents, each citing the PR that set it |
| [`.github/instructions/music-assistant-cross-repo.instructions.md`](./.github/instructions/music-assistant-cross-repo.instructions.md) | when a change touches API commands, shared models or `API_SCHEMA_VERSION` |
| [`.claude/skills/ma-upstream-standards/`](./.claude/skills/ma-upstream-standards/SKILL.md) | on demand: upstream `DEVELOPMENT.md`, Usage Policy, AI Policy and the controller architecture READMEs (players, queues, streams, cache, …) |
| [`.claude/skills/ma-review-pr/`](./.claude/skills/ma-review-pr/SKILL.md) | when reviewing a PR |
| [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) | review standards used by Copilot |

Everything under `.github/instructions/` and `.claude/skills/` is mirrored
verbatim from upstream by `ma-provider-tools` (weekly sync). Do not edit it
here.

## AI Policy Alignment

This provider follows two layered AI policies:

- The Open Home Foundation **upstream policy** —
  [`music-assistant/.github/AI_POLICY.md`](https://github.com/music-assistant/.github/blob/main/AI_POLICY.md)
  — governs everything that lands in `music-assistant/server`.
- The **ecosystem policy** —
  [`trudenboy/ma-provider-tools/AI_POLICY.md`](https://github.com/trudenboy/ma-provider-tools/blob/main/AI_POLICY.md)
  — governs work inside `trudenboy/ma-provider-*` and the upstream boundary
  mechanics.

A per-provider summary lives in [`AI_POLICY.md`](./AI_POLICY.md) (rendered
from `wrappers/AI_POLICY.md.j2`).

Operational rules for AI assistants working in this repo:

1. **A human owns every PR.** The contributor must be able to explain every
   change in their own words; PRs that look like unreviewed AI output are
   closed. AI may be change title or description of pr.
2. **Never open, push to, comment on, or close anything in `music-assistant/*`
   directly.** The only path is the `upstream-pr.yml` workflow, which opens
   the PR as a draft with a human-attestation checklist.
3. **Replies to human reviewers are written by humans.** AI may prepare drafts, polish
   grammar and clarity; This applies only in upstream PRs **not** in our own provider-repo PRs.
4. **Replies to AI review comments may be AI-drafted.** GitHub Copilot,
   code-scanning bots, and similar tools post AI output; replying with
   AI-drafted text is allowed because the conversation is AI ↔ AI. The
   contributor must still read the AI's reply and apply judgement before
   posting. **If a human reviewer joins the same thread, rule 3 takes over
   from that point on** — every reply after that human comment must be
   human-written.
5. **AI co-author trailers** (`Co-Authored-By: <agent> ...`) are encouraged
   in this repo's commits as honest disclosure. Use the identity of the agent
   that actually did the work — e.g. `Co-Authored-By: Cursor
   <cursoragent@cursor.com>`, `Co-Authored-By: Claude <model>
   <noreply@anthropic.com>`, or the line your tool documents. Do **not** copy
   another tool's example trailer, invent a model string, or duplicate a
   trailer your environment already injects. Wrong attribution is worse than
   omitting the trailer. AI-agent trailers are stripped at the upstream
   boundary by `upstream-pr.yml.j2` so they don't appear in
   `music-assistant/server` history; **human** `Co-Authored-By` trailers are
   collected from the synced commit range and appended to the sync commit,
   so contributor credit survives the squash into upstream.

## Upstream vs Ecosystem Conventions

Upstream text below (and in the mirrored files) is written for the
`music-assistant/server` repo. Inside this provider repo, read it through
this mapping. Where the two conflict, this section wins **here**. Upstream's
rules still govern anything that lands upstream.

| Upstream says | In this repo |
|---|---|
| `music_assistant/providers/yandex_music/` | `provider/` |
| `tests/providers/yandex_music/` | `tests/` |
| `scripts/setup.sh`, `pytest`, `pre-commit` from the server root | the commands under *Development Commands* |
| PR titles carry no Conventional Commit prefix | **commits and provider-repo PR titles use Conventional Commits** (`feat:` drives *Feature Specification Discipline*). Upstream PR titles have no prefix, and `upstream-pr.yml` generates them that way |
| PR bodies follow the upstream template only | provider-repo PRs follow `.github/PULL_REQUEST_TEMPLATE.md`. Only upstream PR bodies follow *Upstream PR Body Format* and `music-assistant-pr-description.instructions.md` |
| never reply on GitHub without consent | same in `music-assistant/*` (AI Policy rule 2). In this repo, Copilot threads may get AI-drafted replies (rule 4) |
| PRs target `dev`; backport labels | PRs target `dev`. Releases and the upstream sync are automated (see *Pull Request Workflow*) |
| check `music_assistant/helpers/` first | same: the helpers come from the installed `music-assistant` package, so import them rather than vendoring copies |

## Upstream Engineering Rules (MUST)

The condensed hard rules from upstream `AGENTS.md`, `DEVELOPMENT.md`, the
[Usage Policy](https://github.com/music-assistant/.github/blob/main/USAGE_POLICY.md)
and the mined review precedents. A deviation is at least a `[PROBLEM]` in
upstream review. The full text, with the PR that set each rule, is in
`.github/instructions/music-assistant-standards.instructions.md`.

**Usage policy.** Breaking any of these gets an upstream PR closed, however
useful the change is otherwise.
- Authenticate as the user and fetch audio the way an ordinary client does.
  Never bypass a subscription tier, regional availability, ads, DRM or
  authentication.
- Keep the service's audio URL inside the server: return it only in
  `StreamDetails`, never on a media item, API result or route.
- Never write decoded provider audio to disk, and never add download, export
  or archive features.
- Put a `Throttler` / `ThrottlerManager` in front of the service API, cache
  repeated lookups with `@use_cache` (per-method TTL) and back off on 429.
  Override `max_concurrent_streams` when the service limits concurrent streams.

**Architecture.**
- Reuse `self.mass.http_session`. Never create a `ClientSession`
  (gate `MA001`).
- Providers are isolated: never touch the database (`MA005`), another
  controller's or the queue's state, or settings directly. Go through the
  controller API, a feature flag or a config entry.
- No N+1 API or DB calls in a listing loop. Listings return compact
  `ItemMapping`s; only get-item endpoints return full objects.
- Parsers are synchronous and IO-free (raw provider data in, MA models out).
- Do auth and setup in `handle_async_init`, not `__init__`.
- Stay event-driven: fix a missing event rather than poll. Use
  `mass.call_later` (with a `task_id` to debounce) and the player
  controller's wait helpers, not sleep loops.
- `StreamDetails` codec, sample rate and bit depth must be accurate. Use
  `ContentType.UNKNOWN` rather than guess.
- Library identity: `item.provider == "library"` means `item_id` is the DB
  id. Never treat `mapping.item_id` as a library id; resolve it.
- A change to the serialized shape of an API model belongs in
  `music-assistant/models`, not in provider code.
- Prefer sane defaults over config options, and hide technical options under
  `category="advanced"`.

**Code quality.**
- Catch specific exceptions. Never swallow errors silently (`MA002`). Raise
  MA's typed exceptions (`MediaNotFoundError`, `LoginFailed`,
  `ProviderUnavailableError`, …) with `raise … from err`, and never return
  `None` to signal failure.
- Use `%s` logger arguments, never pre-formatted messages (`MA003`). Never
  log credentials. Mask secure config values.
- Keep a reference to every background task, cancel it on unload, and run
  teardown in `finally` (`MA004`). `self.mass.create_task` tracks tasks for
  you.
- Pin provider requirements exactly in `manifest.json` (`MA006`).
- Never hardcode a limit a real user can exceed. Never depend on set
  ordering.
- Validate user-supplied filesystem paths with `helpers/security.py`
  `is_safe_path`.

**Data and process.**
- Config entries and stored rows are live user data. When a change alters
  stored data, **ask the developer how to migrate before calling the work
  done**. A migration is idempotent, survives half-written values and never
  raises.
- Fix the root cause in the owning layer. Choose the simplest solution;
  keep PRs small and single-purpose.
- New provider structure follows upstream's `_demo_*_provider` templates:
  `__init__.py`, `constants.py`, `helpers.py`, `provider.py` for large
  providers.

## Development Commands

- `./scripts/setup.sh` — initial setup (venv via `uv`, dependencies, pre-commit hooks). Re-run after pulling latest code.
- `uv run pytest` — run all tests
- `uv run pytest tests/<file>.py` — run a specific test file
- `uv run ruff check provider/` — lint
- `uv run ruff format provider/` — auto-format
- `uv run mypy provider/` — type check
- `pre-commit run --all-files` — full pre-commit gate

Always run `pre-commit run --all-files` after a code change to ensure the new
code adheres to the project standards.

## Code Style

### Method Order

Private methods (single/double underscore, non-dunder) must live at the
**bottom** of each class: once a private method appears, every later method in
the class body must also be private. This is upstream music-assistant/server's
AGENTS.md rule, enforced locally by the `check-method-order` pre-commit hook
(`scripts/check_method_order.py`, distributed from ma-provider-tools — do not
edit). Violations that only surface at the upstream PR are exactly what this
hook exists to prevent.

### Comments and Docstrings

Follow upstream's *Code Style* (see *Upstream Agent Guide* below): comment
only complex blocks, keep existing author comments, and write caller-facing
Sphinx docstrings (`:param:`), with the summary on the line after the opening
`"""`. AI assistants tend to generate Google-style (`Args:`) by default, so
rewrite anything that slips through.

### Upstream Rule Gate

`scripts/check_upstream_rules.py` (pre-commit hook `check-upstream-rules`,
distributed from ma-provider-tools; do not edit) **blocks** the upstream
review rules that no linter enforces: `MA001` new `ClientSession`, `MA002`
silently swallowed broad `except`, `MA003` pre-formatted log message, `MA004`
discarded task, `MA005` database access, `MA006` unpinned manifest
requirement. Fix the code. When an exception is genuinely deliberate, add
`# ma-allow: MA00X <reason>` on the reported line (or as a comment line
directly above it); the reason is mandatory
and reviewers check it.

## Branching and PRs

- All work-in-progress PRs target `dev` (primary development branch).
- Before opening a PR: run lint + tests + `pre-commit run --all-files`. CI runs `ruff format --check`, so pushing without `ruff format` is the most common red build.

## Pull Request Workflow

All non-trivial changes go through a pull request — never push directly to
`dev`. Inside a PR, follow this loop:

1. **Self-review.** Run at least one self-review pass on the diff (e.g. the
   `/code-review` skill or an equivalent reviewer) before asking for human
   review.
2. **Copilot triage.** Check the PR for GitHub Copilot review comments. For
   each comment: analyze it, apply a fix when warranted, reply with a short
   justification, and resolve the thread. Copilot is an AI reviewer, so
   AI-drafted replies are allowed here (see *AI Policy Alignment*, rule 4).
   Replies to a **human** reviewer chiming into the same thread must be
   human-written from that point on.
3. **Changelog (+ maintainer-owned version).** *After* review feedback is
   addressed, add a `CHANGELOG.md` entry following the rules in **Changelog
   Discipline** below — in the same PR. The `VERSION` file is **owned by the
   maintainer** (`.github/CODEOWNERS`) and protected on `dev`:
   do **not** bump it in a contributor PR — a `VERSION` change requires the
   maintainer's Code-Owner approval to merge. The maintainer sets the version
   (typically at merge/release time, matching the changelog entry), and the
   release pipeline tags and publishes automatically when the new `VERSION`
   lands on `dev`.
4. **Ask before merging.** Always request explicit maintainer approval to
   merge. Do not self-merge or enable auto-merge without it. (Auto-merge is
   reserved for `distribute.yml`-generated wrapper-sync PRs from
   `ma-provider-tools`.)

Follow-up commits driven by review (your own pass or Copilot's) land directly
on the PR branch — no separate PR needed.

## Upstream is Read-Only

Never push to or open PRs against the upstream Music Assistant repo
(`music-assistant/server` — the true upstream) or the integration fork
(`trudenboy/ma-server`) without an explicit maintainer instruction. The
provider repo is the source of truth; sync to the integration fork and
upstream PR submission run automatically through `ma-provider-tools`
workflows (`sync-to-fork.yml`, `upstream-pr.yml`).

**Reverse-sync (incoming).** Contributions made *upstream* against the inlined
provider (someone editing `music_assistant/providers/yandex_music/` directly in
`music-assistant/server`) are detected and ported back here automatically by the
`ma-provider-tools` reverse-sync radar. They arrive as **draft** PRs on a
`reverse-sync/<domain>-pr<N>` branch, crediting the upstream author via
`Co-authored-by`. A conflict is always visible in the title as
**`[needs-human]`** even if label application fails. The draft contains actual
ported changes plus only real `<<<<<<<` snapshot-merge markers. The radar
compares the upstream PR's normalized base/head snapshots with the current
provider files; patch-index SHAs and `git apply` are not part of the merge.
A scaffold-only PR is forbidden. Resolve the listed artifacts, drop the
`needs-human` label, and treat it like any other PR (review, changelog,
maintainer approval). Automatic retries update only untouched bot-owned
scaffold drafts; they never overwrite a PR with human commits or provider/test
changes. `VERSION` / `translations/en.json` are never touched by reverse-sync;
bump them as usual. Do **not** manually re-port a change the radar already
opened a PR for.

This provider is intended to be inlined into
`music_assistant/providers/yandex_music` upstream eventually — that is the
target shape, not a possibility. Any code that lints / type-checks here
must lint / type-check identically upstream.

## Upstream PR Body Format

When drafting or refining text for an upstream PR body in
`music-assistant/server`, the body MUST follow upstream's
[`PULL_REQUEST_TEMPLATE.md`](https://github.com/music-assistant/.github/blob/main/.github/PULL_REQUEST_TEMPLATE.md)
skeleton, in this order:

1. `# What does this implement/fix?` — narrative goes under this heading.
2. `**Related issue (if applicable):**`.
3. `## Types of changes` — tick **exactly one** box. Upstream's
   `PR Labels` check fails with "Tick exactly one" when several are
   ticked. For a release that mixes types, pick the dominant one.
4. `## Checklist`. The `I have read and complied with the project's
   AI Policy` checkbox is the human-attestation checkpoint; do not
   append a separate attestation block.

Upstream's `pr-labels.yaml` reads the ticked `## Types of changes`
checkbox to apply its single label; the release-notes generator slots
by label. A body without these sections silently breaks both.

Per *AI Policy Alignment* rule 2, do not edit the upstream PR
directly — produce the corrected body and the human applies it
(via `gh api repos/music-assistant/server/pulls/<N> -X PATCH -F body=@file.md`).

## Auto-Synced Lint & Typing Config

`ruff.toml`, `[tool.mypy]`, and `[tool.codespell].skip` mirror upstream
`music-assistant/server/pyproject.toml` and are regenerated by
`ma-provider-tools` (`scripts/sync_upstream_config.py`, weekly cron).
**Do not hand-edit these in the provider repo** — the
`Check config sync` GitHub Action will fail any PR that drifts. To change
a rule, open a PR in `trudenboy/ma-provider-tools`; once merged, the
distribute workflow propagates the change here.

Provider-specific carve-outs that do *not* drift: `python_version`,
`packages = ["tests", "provider"]`, the `[[tool.mypy.overrides]]`
block, and `codespell.ignore-words-list`.

Repo-level metadata also flows through `ma-provider-tools` (fields
`github_description`, `github_topics`, `github_homepage`,
`related_providers` in `providers.yml`). They drive the GitHub "About"
block, the auto-synced README badge / quick-links / cross-links header
(between `<!-- >>> ma-provider-tools sync (readme header) >>> -->`
markers), and the docs-site landing hero. Do not edit GitHub repo
settings directly — open a PR in `ma-provider-tools` instead.

The **Music Assistant** badge in the README is a dynamic shields.io
endpoint hosted at
`https://trudenboy.github.io/ma-provider-tools/badges/<domain>.json`. A
4-hour cron in `ma-provider-tools` (`update-ma-version-badges.yml`)
refreshes the JSON to show which MA channel (stable / beta / dev) ships
the provider and at what MA version. The provider's own version pin is
included once a `VERSION` file has been synced alongside `manifest.json`
in each channel via the existing `sync-to-fork` / `upstream-pr`
workflows. Do not edit the badge URL or the JSON manually.

## Feature Specification Discipline

Non-trivial features go through a written spec before code. The template
lives at `specs/feature-spec.md` (auto-synced from
`ma-provider-tools/wrappers/feature-spec.md.j2` — do not edit it in
place; changes go through `ma-provider-tools`).

- **When required.** Every PR whose Conventional-Commit type is `feat:`
  MUST add a new file `specs/<state>/<NNNN>-<kebab-slug>.md` derived
  from the template. Types `fix:`, `chore:`, `docs:`, `test:`,
  `refactor:`, `perf:`, `build:`, `ci:` are exempt. When a borderline
  `feat:` legitimately needs no spec (e.g. a pure wire-up, a one-line
  enum addition), state *"no spec required because <reason>"* in the
  PR body so reviewers can confirm.
- **Enforcement.** P0 (now): this is a documented rule that AI agents
  and reviewers uphold. P1 (next release cycle): the rule is promoted
  to a hard CI gate after observing false-positive patterns.
- **T-shirt sizing** — the `size:` frontmatter declares the required
  artifacts:
  - **S** (≤ 10 min effort): Problem Statement + Acceptance Criteria
    (≥ 5 bullets) + Test Plan.
  - **M** (10–20 min): S + Sequence Diagram.
  - **L** (> 20 min): M + Data Model.
- **WIP = 1.** At most one spec lives in `specs/inprogress/` at any
  time. Move it to `specs/done/` (or revert to `specs/todo/`) before
  starting the next.
- **Numbering.** Zero-padded 4-digit (`0001`, `0002`, …), monotonic
  per repo. Gaps are fine.
- **Optional `feature_id:`** in the frontmatter links the spec to a
  `ProviderFeature` enum member. When set, the `Check feature
  consistency` workflow cross-validates against `SUPPORTED_FEATURES`
  in this repo and against the corresponding `providers.yml`
  `features[].feature_id` entry in `ma-provider-tools`. A mismatch
  fails CI.
- **Idempotency.** All changes flow through the spec — no
  "I'll patch it in copilot mode and update the spec later". If the
  implementation diverges from the spec, update the spec **in the
  same PR**.

## Test-Driven Development

Use **red / green / refactor** TDD for all new features and bug fixes:

1. **Red.** Write the test first. Confirm it **fails** before writing
   implementation.
2. **Green.** Write the **minimal** code to make the test pass.
3. **Refactor.** Clean up the implementation while keeping tests green.

### Rules for AI agents

- **Never modify existing tests to make them pass.** If a test fails, fix
  the implementation. If a test is genuinely wrong, explain why in the
  commit message before changing it.
- **Never write tautological tests** — tests that reimplement the logic
  under test locally and assert on that local copy. Always call the real
  function / method.
- **Test real behaviour, not mocks.** Avoid over-mocking: if a test only
  verifies that mocks return what they were configured to return, it
  tests nothing. For Music Assistant providers this means: prefer real
  fixtures (`tests/fixtures/*.json`) and `syrupy` snapshots over hand-
  rolled mock graphs whenever the parser / mapper under test is pure.
- **Every test must be able to fail.** If removing the implementation
  doesn't break the test, the test is useless.
- **Bug fix flow.** First write a test that **reproduces** the bug
  (red), then fix it (green). The reproducer becomes the regression
  guard.

### Standalone-only tests

`tests/` is exported to `music-assistant/server` together with the
provider. Tests that only make sense in this repo, such as checks on
`pyproject.toml`, `uv.lock` and `scripts/` or on provider-local docs,
belong in `tests/standalone/`. The sync and upstream-PR workflows never
export that directory, so upstream does not get code that is not part of
the server project. Do not use a module-level `pytest.skip` guard to keep
such a test quiet upstream; move it to `tests/standalone/` instead.

## Changelog Discipline

`CHANGELOG.md` follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and is the
input the release pipeline reads when it composes GitHub Release notes.
Treat the rules below as falsifiable invariants — fix the entry, do not
relax the rule.

- **Bare canonical headings only.** Use `### Added`, `### Changed`,
  `### Deprecated`, `### Removed`, `### Fixed`, `### Security` —
  nothing else. No `### Improved`, `### Refactored`, `### Tests`, no
  trailing prose like `### Fixed — long sentence`.
- **Canonical order.** Inside each version block, categories appear in
  this order: Added → Changed → Deprecated → Removed → Fixed → Security.
  Skip categories that are empty; never reorder.
- **No private symbols, no internal paths in bullets.** Forbidden:
  `_underscore_func`, `provider/foo.py`, `ClassName.method`. Allowed:
  uppercase config keys (e.g. `CONF_QUALITY`), backticked user-facing
  filenames (`` `pyproject.toml` ``, `` `manifest.json` ``), markdown
  links. Internal paths rot through refactors — describe what the
  **user** observes instead.
- **No process-noise headings or bullets.** Things like `Code-review
  polish`, `Round 2 fixes`, `Copilot review on PR #N`, `Tests`,
  `Internal` belong in `git log`, not the changelog. If a review
  surfaced a real bug, file it under `### Fixed`.
- **No prose between `## [version]` and the first `### Category`.**
  Release-note tooling collects bullets that appear *after* the first
  category heading; intro paragraphs are silently dropped.
- **One entry per version.** For the release that lands these changes
  (`X.Y.Z` → `X.Y.(Z+1)`), add a single `## [X.Y.(Z+1)] - YYYY-MM-DD`
  block above the existing top-most version, populated with the categories
  the PR touches. Do not retroactively edit older version blocks. The
  matching `VERSION` bump is applied by the maintainer (see *Pull Request
  Workflow* step 3).

## Upstream Agent Guide (verbatim)

Upstream `music-assistant/server` `AGENTS.md`, mirrored verbatim (headings
shifted down one level). It covers behaviour, the Usage Policy, code style,
migrations, debugging (logs and the read-only `library.db`) and provider
mappings. Read it through *Upstream vs Ecosystem Conventions* above.

Music Assistant is an async Python music library manager that connects to streaming services and speakers, integrating with Home Assistant.

### Behaviour

- NEVER automatically reply on Github (PR's or Discussions) without explicit consent from the developer.

### Usage policy

Music Assistant streams music to the user's own speakers. It is not a way to download or keep
copies of it, and we do not accept changes that make it one — see the
[Usage Policy](https://github.com/music-assistant/.github/blob/main/USAGE_POLICY.md).

Flag it in review, and never write it yourself, when a change would:

- expose a music service's own audio URL to anything outside the server (an API result, a
  media item, or a route that hands it to a caller)
- decode protected audio outside what the user's own account is entitled to, or keep the
  decoded result rather than only playing it
- call a service's API without throttling, or re-fetch what the cache already holds
- write decoded audio from a streaming provider to disk
- bypass a subscription tier, regional availability, or a service's stated concurrent-stream
  limit (see `max_concurrent_streams` in `music_assistant/models/music_provider.py`)
- add downloading, exporting, or archiving of provider audio, however it is framed

Some guards in the codebase exist only for this reason and read as removable if you do not know
that — the readrate pacing on the stream endpoints, and the filesystem-only restriction on
background audio analysis. Leave them in place. `DEVELOPMENT.md` carries the same rules for
provider authors.

### Development Commands

- `scripts/setup.sh` - Initial setup (venv, dependencies, pre-commit hooks). Re-run after pulling latest code.
- `pytest` - Run all tests (add `-n auto --dist loadfile` to run in parallel)
- `pytest --cov music_assistant` - Run all tests with coverage
- `pytest tests/specific_test.py` - Run a specific test file
- `pre-commit run --all-files` - Run all pre-commit hooks
- `python -m music_assistant --log-level debug` - Run server locally (localhost:8095)
- Requires ffmpeg v7.0+ and Python 3.14+ (see `.python-version` for the pinned runtime)

Always run `pre-commit run --all-files` after a code change to ensure the new code adheres to the project standards.

### Provider Development

Providers are modular: music (sources), player (speakers), metadata (art/lyrics), plugin (extras). See `_demo_*_provider` directories for annotated templates when creating new providers.

Each provider has at least `__init__.py` (logic) and `manifest.json` (metadata/config schema).

Check `helpers/` for reusable utilities before writing new ones.

### Code Style

#### Comments

Only use comments to explain complex, multi-line blocks of code. Do not comment obvious operations. Inline comments in the code are there to explain code parts that need explaining, keep that in mind yourself when writing code but also respect existing comments from authors - they apparently had a reason to write the comment, dont remove them unless needed.

#### Docstring Format

Use Sphinx-style docstrings with `:param:` syntax. For simple functions, a single-line docstring is fine.
Don't explain inner workings of the code in the docstrings (you can use inline comments for that if/when needed). The docstring should provide clarity to the caller of the function/method, not explain how it works technically/internally. Use our preference for multi line docstrings where the first line starts on the next line:

```python
def my_function(param1: str, param2: int, param3: bool = False) -> str:
    """
    Brief one-line description of the function.

    :param param1: Description of what param1 is used for.
    :param param2: Description of what param2 is used for.
    :param param3: Description of what param3 is used for.
    """
```

Do **not** use Google-style (`Args:`) or bullet-style (`- param:`) docstrings.

#### File structure
Private methods should be at the bottom of the file, public at the top.

### Data changes need migrations

Config entries and database rows are live user data. A renamed key, a changed type, a value that
moves scope, a dropped column. None of it fails a test and none of it hurts a new install. It only
breaks the installs that already hold data, and table creation code never repairs those.

So when a change touches stored data, do not decide alone and do not leave it for the PR. Ask the
developer in the session with an AskUserQuestion popup, along the lines of "the code we touch needs
a migration, how do you want to handle it?", before treating the work as done.

A migration step runs once, against data written by a version you cannot inspect. Make it
idempotent, let it survive missing and half-written values, and never let it raise. A failed
library migration resets the database and costs the user a full rescan.

### Branching and PRs

- All PRs target `dev` (primary development branch). `stable` is for production releases.
- PRs labeled `bugfix` + `backport-to-stable` are automatically backported to `stable` — use only for bugs also present in `stable`.
- Backporting a **schema change** permanently diverges `DB_SCHEMA_VERSION` between the branches and needs an extra dev-side guard migration; see `music_assistant/controllers/music/README.md`.

### Debugging

MA stores its data in `$HOME/.musicassistant/`. When debugging locally:

- **Logs:** `$HOME/.musicassistant/musicassistant.log` (current), `musicassistant.log.1`, `.log.2`, etc. for older rotated logs.
- **Database:** `$HOME/.musicassistant/library.db` — query via `sqlite3`. **Only execute SELECT queries** — never write to a live database.

#### Provider Mappings

Every `MediaItem` (track, album, artist, playlist) has a `provider_mappings` attribute containing the exact mappings of the item on (each) provider. For a MediaItem that comes from a musicprovider directly, this will usually contain one single ID-mapping (although it is possible that a provider has multiple mappings). For library items, this will contain all mappings of all providers connected to the item.

The ProviderMapping has this structure:

- `item_id` (str): The music provider's item ID (e.g., `"spotify--track123"`)
- `provider_domain` (str): The musicprovider's domain (e.g., `"spotify"`, `"apple_music"`, `"tidal"`)
- `provider_instance` (str): The provider instance ID (to handle multiple instances of the same provider).
- some more details such as the quality (relevant in case of album or track)

**Important patterns:**

- A media item itself also has an item_id and provider attribute. For an item that comes straight from the musicprovider itself (so not from the MA library) the provider attribute will be set to the instance_id of that provider.
- Library items are identified by `item.provider == "library"` where `item.item_id` is the library DB ID
- `provider_domain='library'` **never exists** in provider_mappings — library items don't have mappings to themselves
- To resolve a provider item to its library equivalent, use: `await mass.music.<mediatype>.get_library_item_by_prov_id(item_id, provider_instance_id_or_domain)`
- Never assume you can use `mapping.item_id` directly as a library DB ID — always use the resolution method above
