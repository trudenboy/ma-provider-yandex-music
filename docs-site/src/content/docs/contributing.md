---
title: Contributing
---

# Contributing

Thank you for your interest in contributing to **Yandex Music**!

## Code of Conduct

Be respectful, inclusive, and professional. We follow the standard open source code of conduct.

## Reporting Bugs

Open a GitHub Issue with:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (MA version, provider version)
- Logs from the MA server

## Suggesting Features

Open a GitHub Issue explaining:
- The use case and problem it solves
- Your proposed solution
- Alternative approaches you considered
- Whether you are willing to implement it

## Pull Requests

1. Fork and clone the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following the [coding standards](development.md#code-quality)
4. Write or update tests (see [Development → Running Tests](development.md#running-tests))
5. Ensure CI passes: `pre-commit run --all-files`
6. Update documentation if your change affects behavior or configuration
7. Push to your fork and open a PR against `dev`

PR description should include:
- What changed and why
- How to test it (manual steps or test names)
- Any gotchas or follow-up work

**This repo is the source of truth.** This provider is also inlined into
[`music-assistant/server`](https://github.com/music-assistant/server) under
`music_assistant/providers/yandex_music/`. If you discover it there and open a
PR against that copy, your change is **not lost** — a reverse-sync bot detects
merged upstream PRs touching this provider and automatically opens a draft PR
porting them back here, crediting you via `Co-authored-by`. Still, the smoothest
path is to contribute **here** (against `dev`), where it lands
without the cross-repo round-trip.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

## Further Reading

- [Testing Guide](testing.md) — running tests locally, CI pipeline, coverage
- [Incident Management](incident-management.md) — labels, issue automation, Copilot triage
- [Docker Dev Environment](dev-docker.md) — run MA + provider locally without dependencies
- [Development](development.md) — dev setup, tooling, code quality standards
