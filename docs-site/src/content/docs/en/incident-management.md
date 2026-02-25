---
title: Incident Management
---

# Yandex Music — Incident Management

## Where to File Incidents

> **File issues here:** [github.com/trudenboy/ma-provider-yandex-music/issues](https://github.com/trudenboy/ma-provider-yandex-music/issues)

Use the **New Issue** button and choose an appropriate template. Do not file issues in `trudenboy/ma-server` or `trudenboy/ma-provider-tools` — those are for different purposes.

## Labels

All issues use a standardized label system:

### Incident Labels

| Label | Color | Description |
|-------|------|---------|
| `incident:ci` | 🔴 | CI/CD failure |
| `incident:release` | 🔴 | Release pipeline failure |
| `incident:sync` | 🟠 | Fork sync failure |
| `incident:bug` | 🔴 | User-reported bug |
| `incident:security` | 🟣 | Security vulnerability |
| `incident:upstream` | 🔵 | Upstream API change |
| `incident:proposal` | 🟢 | Improvement proposal or new feature |

### Priority Labels

| Label | Description |
|-------|---------|
| `priority:critical` | Blocks operation, requires immediate action |
| `priority:high` | Important, needs to be addressed soon |
| `priority:medium` | Normal queue |
| `priority:low` | Nice to have, not urgent |

### Special Labels

| Label | Description |
|-------|---------|
| `copilot` | Route the issue to the GitHub Copilot agent |

## Automated Incident Pipeline

Many incidents are created automatically without manual intervention:

### CI Failures

1. Tests or linters fail in `test.yml`
2. `reusable-report-incident.yml` creates an issue with labels `incident:ci` + `priority:high`
3. If an open issue for this type of failure already exists — a comment is added (no duplicates)
4. The issue is automatically added to the MA Ecosystem project board

### Other Automated Incidents

| Event | Label |
|---------|-------|
| Fork sync failure | `incident:sync` |
| Security audit failure | `incident:security` |
| Release pipeline failure | `incident:release` |

## GitHub Project Board (MA Ecosystem)

All issues with `incident:*` labels are automatically added to the project board:

- **Addition**: `issue-project.yml` triggers on issue creation or label change
- **Provider field**: set automatically for Yandex Music
- **Release tracking**: `reusable-release.yml` creates a draft issue in the project on each release

## Copilot Triage

Any issue can be routed to the GitHub Copilot agent for automated analysis:

1. Add the `copilot` label to the issue
2. `copilot-triage.yml` automatically assigns `@copilot`
3. Copilot analyzes the issue and may create a PR with a fix

This is useful for routine bugs, documentation typos, and small improvements.

## Creating Incidents Manually

Use issue templates to create incidents manually:

| Template | When to use |
|--------|-------------------|
| **Bug report** | Reproducible bug — attach the `incident:bug` label |
| **Upstream API change** | Upstream Yandex / KION / Zvuk API changed — label `incident:upstream` |
| **Improvement proposal** | New feature proposal — label `incident:proposal` |

After creating the issue, add a priority label if needed.
