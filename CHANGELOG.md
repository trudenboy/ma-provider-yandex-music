# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- changelog entries will be added here by release workflow -->

## [2.6.7] - 2026-02-27

- refactor: extract _decrypt_response_stream to fix PLR0915 (`f8cc382`)
- fix: address PR review comments — URL refresh improvements (`54ad23e`)
- test: update playlist snapshots for supported_mediatypes field (`08f8f63`)
- chore: skip docs-site/package-lock.json in codespell (`bbcebf5`)
- fix: use _track_id_from_item_id helper in _refresh_encrypted_url (`010db22`)
- fix: raise max_retries from 5 to 6 for encrypted stream (`6a7469a`)
- docs: document Yandex CDN ~6-7 MB per-connection limit and 6-retry coverage (`3893225`)
- fix: fix infinite loop bug on 4xx URL refresh in windowed stream loop (`5eb8a33`)
- feat: replace open-ended Range requests with 4 MB windowed streaming (`f86e4fd`)
- docs: remove CDN limitation section, streaming now uses 4 MB windows (`fc9a814`)
- chore: sync workflow wrappers from ma-provider-tools (#64) (`d8e11b9`)

---

## [2.6.6] - 2026-02-26

- fix: prevent lossless playback interruptions without buffering (`2b2d630`)
- fix: harden encrypted stream against more failure modes (`d4cc27f`)
- fix: raise max_retries from 3 to 5 for encrypted stream (`6b3b2e6`)

---

## [2.6.5] - 2026-02-26

- fix: address PR review comments on throttling (`1887dd7`)

---

## [2.6.4] - 2026-02-26

- chore: sync workflow wrappers from ma-provider-tools (#61) (`77dd47d`)
- docs: add Starlight index page (`db17ee4`)
- docs: add configuration page (`147a341`)
- docs: add my-wave feature page (`3f3e049`)
- docs: add lyrics feature page (`0fe8704`)
- docs: add picks-and-mixes feature page (`853c796`)
- docs: add browse feature page (`b06c58b`)
- docs: add audio-quality feature page (`915221a`)
- chore: add package-lock.json for npm cache (`5f932a3`)
- docs: add Starlight title frontmatter to contributing.md (`8bfc084`)
- docs: add development.md (dev environment guide) (`4c502e4`)
- docs: add provider icon emblem to index page (`4faec66`)
- docs: обновление пользовательской документации (#62) (`19d4c1c`)
- docs: добавить способ получения токена из десктопного клиента (#63) (`9af7301`)
- fix(docs): исправить форматирование таблицы на странице radio (`6226490`)
- docs: добавить ссылку на библиотеку и дисклеймер на главной странице (`eff8325`)
- docs: упростить дисклеймер на главной странице (`3aba38f`)
- docs: добавить английские переводы всех страниц документации (`7d1e100`)
- docs: сделать Music Assistant ссылкой на официальный сайт (`e6bb739`)
- Reorder and update Yandex Music provider information (`f336914`)
- Change warning to caution in disclaimer section (`674f8d3`)
- Add subscription note for Yandex Plus (`a756ffe`)
- Fix markdown syntax for caution block (`aab1d30`)
- Revise disclaimer for unofficial Yandex Music provider (`65c0259`)
- feat: add request throttling and rate-limit detection (`a6883f2`)
- feat: throttle _call_no_retry (rotor feedback) via shared Throttler (`2201dd4`)
- chore: remove redundant ruff.toml and ignore docs-site/node_modules (`3597f16`)
- chore: add docs-site/node_modules to gitignore, trim trailing newlines (`501f72d`)

---

## [2.6.3] - 2026-02-24

- feat: add WEB_BASE_URL constant for web UI links (`413d616`)
- refactor: use WEB_BASE_URL constant in parsers instead of hardcoded URLs (`7820b16`)

---

## [2.6.1] - 2026-02-24

- fix: use DEFAULT_BASE_URL constant in description string (`7cca832`)

---

## [2.5.9] - 2026-02-24

No changes.

---

## [2.5.8] - 2026-02-24

No changes.

---

## [2.5.7] - 2026-02-24

- chore: sync workflow wrappers from ma-provider-tools (#59) (`25dbf7b`)

---

## [2.5.6] - 2026-02-24

- Refactor/yandex config categories (#50) (`500de64`)
- chore: sync workflow wrappers from ma-provider-tools (#51) (`6069c9e`)
- chore: sync workflow wrappers from ma-provider-tools (#52) (`4c8d318`)
- chore: sync workflow wrappers from ma-provider-tools (#53) (`071d2f7`)
- chore: generate historical changelog [skip ci] (`4e39430`)
- docs: add pre-separation upstream PR history to CHANGELOG (`df2bb6a`)
- chore: sync workflow wrappers from ma-provider-tools (#54) (`c545e94`)
- chore: sync workflow wrappers from ma-provider-tools (#55) (`694565f`)
- docs: remove FLAC streaming modes and buffer size documentation (#56) (`df58fed`)
- chore: sync workflow wrappers from ma-provider-tools (#57) (`f926e41`)
- chore: sync workflow wrappers from ma-provider-tools (#58) (`fe49532`)

---

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
