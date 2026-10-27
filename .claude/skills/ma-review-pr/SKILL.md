---
name: ma-review-pr
description: Use when asked to review a pull request in this provider repo (or a PR link is shared) — applies the upstream music-assistant/server review standards with this repo's exceptions
---

<!-- ma-provider-tools: rendered from wrappers/.claude/skills/ma-review-pr/SKILL.md.j2 — do not edit -->

# Review a Pull Request

Review the GitHub pull request: $ARGUMENTS.

This follows upstream `music-assistant/server`'s `review-pr` skill. The review
is read-only: report findings in the console. Never post comments, approve,
request changes or modify the code under review.

## Steps

1. `gh pr view` for the PR details and description.
2. Create a git worktree and do everything below inside it, so the checked-out
   branch stays untouched (`git worktree add --detach <path>`).
3. `gh pr checkout` in the worktree, then confirm the local commit hash
   matches the remote PR head.
   - **HARD STOP**: if the checkout fails, or the hashes still differ, stop
     and report it. No workarounds: no `git fetch`, no reviewing from the diff
     alone. Wait for instructions.
4. `gh pr checks` for CI status.
5. `gh pr diff` for the changes, then read the surrounding code for anything
   the diff alone can't settle.
6. Apply, in this order:
   - `REVIEW_STANDARDS.md` in this directory (upstream, verbatim). Its
     `CLAUDE.md` is this repo's `AGENTS.md` (symlink), and provider specifics
     are in `CLAUDE.local.md`.
   - The provider-repo exceptions at the top of
     `.github/copilot-instructions.md` (paths, Conventional Commit titles,
     PR template, checks already settled by CI).
   - The precedents in
     `.github/instructions/music-assistant-standards.instructions.md`. Cite
     the linked upstream PR when you raise one.
   - `references/new-provider.md` when the PR adds a provider. The demo
     providers live in the installed `music-assistant` package
     (`music_assistant/providers/_demo_*_provider`).

Running tests or linters isn't part of this; CI does that.

## Output Format

Comments per file and line that need attention. Skip what's already fine.

Each comment carries a severity (`[CRITICAL]`, `[PROBLEM]`, `[SUGGESTION]`),
states the problem in a sentence, says why it matters when that isn't
self-evident, and gives a concrete fix or snippet.

Close with an overall assessment (`approve`, `request changes` or `comment`)
followed by the findings grouped by severity.
