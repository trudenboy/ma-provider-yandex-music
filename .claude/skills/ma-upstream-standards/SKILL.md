---
name: ma-upstream-standards
description: Use when designing, implementing or reviewing provider code that touches Music Assistant architecture — streaming and StreamDetails, players and queues, caching and throttling, config entries and migrations, discovery, the webserver/API contract, the manifest — or when unsure what upstream music-assistant/server accepts
---

<!-- ma-provider-tools: rendered from wrappers/.claude/skills/ma-upstream-standards/SKILL.md.j2 — do not edit -->

# Upstream Music Assistant Standards

The upstream documents behind the MUST list in `AGENTS.md`, mirrored verbatim
from `music-assistant/server` and `music-assistant/.github` by
`ma-provider-tools` (weekly sync). Read only the parts the task needs; they
are long. Paths inside them are upstream paths: map
`music_assistant/providers/yandex_music/` to `provider/` and
`tests/providers/yandex_music/` to `tests/`.

| Read | When |
|---|---|
| `references/USAGE_POLICY.md` | anything that fetches, decodes, caches or exposes audio, or calls the service API |
| `references/DEVELOPMENT.md` | provider structure, `get_stream_details` / `get_audio_stream`, streaming-provider rules, the manifest schema |
| `references/AI_POLICY.md`, `references/CONTRIBUTING.md` | anything that will be submitted upstream |
| `references/controllers/<name>.md` | how a core controller works before relying on it (start with `music`, `cache`, `metadata` and `streams`) |
| `.github/instructions/music-assistant-standards.instructions.md` | the full review precedents, each citing the upstream PR that set it |
| `.github/instructions/music-assistant-cross-repo.instructions.md` | API commands, shared models (`music-assistant/models`), `API_SCHEMA_VERSION` |

Upstream wins on what is accepted upstream. For how work is done in this repo
(commits, PRs, releases, the upstream sync), `AGENTS.md` wins.
