# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2026-02-24

- Refactor/yandex config categories (#50) (`500de64`)

## 2026-02-21

- fix: add mass fixture to conftest.py and remove stale type: ignore (`62ebd9d`)
- fix: fix ruff import sort in tests/common.py (`eae9d6a`)
- fix: bump music-assistant-models to 1.1.99 and add tests/common.py (`6a44330`)
- docs: unify documentation structure (#16) (`bb8827b`)

## 2026-02-19

- fix(streaming): fix FLAC seek, remove direct/preload modes (`388a3cd`)
- feat: initial provider setup (`d5cf489`)


<!-- Pre-separation: development in trudenboy/ma-server monorepo -->
<!-- The following changes were developed in the `trudenboy/ma-server` monorepo before this provider was extracted into its own repository on 2026-02-19. -->

## 2026-02-17

- fix: validate tags via API before showing in browse and recommendations
- fix: fix LRC regex, HMAC sign construction, and temp file cleanup order
- fix: fix race conditions, dead code, caching bugs, and performance issues
- fix: fix exception handling, docstring, and log noise in provider

## 2026-02-16

- fix: drastically reduce config entries and simplify configuration
- fix: fix critical review issues: rename key_base64, fix double close, add temp file cleanup
- fix: fix streaming issues: FD leak, buffered fallback, size limits, task cleanup, stale files
- fix: fix AAC codec mapping, caching issues, and datetime timezone awareness
- fix: fix Picks & Mixes: use dynamic tag discovery, filter empty/useless tags
- fix: fix browse: "Invalid subpath" error and empty tag folders
- fix: increase Discovery initial tracks from 5 to 20
- test: add comprehensive test coverage for recommendation methods
- test: restore test_recommendations.py with mypy return type annotations

## 2026-02-12

- feat: add My Wave visibility toggle settings

## 2026-02-09

- feat: add My Wave (Моя волна) Browse folder
- fix: fix playlist loading and missing album cover art (music-assistant/server#3099)

## 2026-02-06

- chore: regenerate parser snapshots after upstream models bump

## 2026-02-05

- fix: fix playlist tracks not loading in UI
- fix: fix missing album cover art in library
- fix: suppress library DEBUG logs to avoid huge API dumps in playlist view
- fix: load playlist tracks reliably and avoid timeouts
- fix: prevent caching of empty playlist results on network errors

## 2026-02-04

- chore: remove lyrics feature support

## 2026-01-28

- feat: add Yandex Music provider (music-assistant/server#3002)

## [2.5.6] - 2026-02-24

## What's Changed
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/1
* Main by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/2
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/3
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/4
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/5
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/12
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/13
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/14
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/17
* docs: unify documentation structure by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/16
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/18
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/20
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/21
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/22
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/23
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/25
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/26
* Refactor/yandex config categories by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/50
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/51
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/52
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/53
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/54
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/55
* docs: remove FLAC streaming modes and buffer size documentation by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/56
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/57
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/58


**Full Changelog**: https://github.com/trudenboy/ma-provider-yandex-music/compare/v2.1.1...v2.5.6

---

## [2.5.7] - 2026-02-24

## What's Changed
* chore: sync workflow wrappers from ma-provider-tools by @trudenboy in https://github.com/trudenboy/ma-provider-yandex-music/pull/59


**Full Changelog**: https://github.com/trudenboy/ma-provider-yandex-music/compare/v2.5.6...v2.5.7

---

## [2.5.8] - 2026-02-24

**Full Changelog**: https://github.com/trudenboy/ma-provider-yandex-music/compare/v2.5.7...v2.5.8

---

<!-- changelog entries will be added here by release workflow -->
