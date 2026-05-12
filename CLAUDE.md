<!-- ma-provider-tools: rendered from wrappers/CLAUDE.md.j2 -->
# CLAUDE.md

This file aligns development of the **Yandex Music** provider with the
upstream [`music-assistant/server`](https://github.com/music-assistant/server)
standards. It is rendered from `wrappers/CLAUDE.md.j2` in
[`trudenboy/ma-provider-tools`](https://github.com/trudenboy/ma-provider-tools)
and is kept in sync across every provider repo — **do not edit it here**.

Provider-specific architecture, key flows, and gotchas live in
[`CLAUDE.local.md`](./CLAUDE.local.md). Claude Code automatically picks up both
files when working in this repository.

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
   closed.
2. **Never open, push to, comment on, or close anything in `music-assistant/*`
   directly.** The only path is the `upstream-pr.yml` workflow, which opens
   the PR as a draft with a human-attestation checklist.
3. **Replies to human reviewers are written by humans.** AI may polish
   grammar and clarity; AI may not draft the substance. This applies in
   upstream PRs **and** in our own provider-repo PRs.
4. **Replies to AI review comments may be AI-drafted.** GitHub Copilot,
   code-scanning bots, and similar tools post AI output; replying with
   AI-drafted text is allowed because the conversation is AI ↔ AI. The
   contributor must still read the AI's reply and apply judgement before
   posting. **If a human reviewer joins the same thread, rule 3 takes over
   from that point on** — every reply after that human comment must be
   human-written.
5. **AI co-author trailers** (`Co-Authored-By: Claude ...`) are encouraged
   in this repo's commits as honest disclosure. They are stripped at the
   upstream boundary by `upstream-pr.yml.j2` so they don't appear in
   `music-assistant/server` history.

## Development Commands

- `./scripts/setup.sh` — initial setup (venv via `uv`, dependencies, pre-commit hooks). Re-run after pulling latest code.
- `uv run pytest` — run all tests
- `uv run pytest provider/tests/<file>.py` — run a specific test file
- `uv run ruff check provider/` — lint
- `uv run ruff format provider/` — auto-format
- `uv run mypy provider/` — type check
- `pre-commit run --all-files` — full pre-commit gate

Always run `pre-commit run --all-files` after a code change to ensure the new
code adheres to the project standards.

## Code Style

### Comments

Only use comments to explain complex, multi-line blocks of code. Do not comment
obvious operations.

### Docstring Format

Use Sphinx-style docstrings with `:param:` syntax. For simple functions, a
single-line docstring is fine.

Don't explain inner workings of the code in the docstrings (you can use inline
comments for that if/when needed). The docstring should provide clarity to the
**caller** of the function/method, not explain how it works
technically/internally.

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
AI assistants tend to generate Google-style by default — explicitly steer them
to Sphinx, and rewrite anything that slips through.

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
3. **Version + changelog.** *After* review feedback is addressed, bump the
   `VERSION` file (PEP 440 — `1.2.0` stable, `1.2.0b1` beta) and add a
   `CHANGELOG.md` entry following the rules in **Changelog Discipline**
   below — in the same PR. The release pipeline tags and publishes
   automatically when the new `VERSION` lands on `dev`.
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

This provider is intended to be inlined into
`music_assistant/providers/yandex_music` upstream eventually — that is the
target shape, not a possibility. Any code that lints / type-checks here
must lint / type-check identically upstream.

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
- **One entry per version.** When the PR bumps `VERSION` from `X.Y.Z`
  to `X.Y.(Z+1)`, add a single `## [X.Y.(Z+1)] - YYYY-MM-DD` block
  above the existing top-most version, populated with the categories
  the PR touches. Do not retroactively edit older version blocks.

## Debugging

Music Assistant stores its data in `$HOME/.musicassistant/`. When debugging
locally:

- **Logs:** `$HOME/.musicassistant/musicassistant.log` (current),
  `musicassistant.log.1`, `.log.2`, etc. for older rotated logs.
- **Database:** `$HOME/.musicassistant/library.db` — query via `sqlite3`.
  **Only execute SELECT queries** — never write to a live database.
