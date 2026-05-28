# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.5.15] - 2026-05-28

### Fixed

- Reduce Yandex smart-captcha risk for users routing through datacenter or VPN IPs. Tag-validation in browse and recommendations used to fire 5–8 parallel `get_tag_playlists` calls per category via `asyncio.gather`. Empirical synthetic probing against the live Yandex backend (4 probes covering sustained RPS, same- and cross-endpoint bursts, and recovery time) found this is harmless on a residential RU IP — Yandex tolerated ≥10 RPS sustained and ≥10 concurrent requests per endpoint without a single 429. On a datacenter / hosted-VPN IP, however, the same burst pattern matched Yandex's scraper-signature heuristic and tripped captcha within ~460 ms. The validation pass was paranoid filtering of evergreen hardcoded tag categories and Yandex's own landing-discovered tags (already pre-filtered server-side); dropping it eliminates the burst entirely. If a tag turns out empty at click time, browse already renders an empty folder.

### Added

- Defense-in-depth: per-endpoint concurrency lock in the API client. Every call through `_call_with_retry` is now also serialised by a lock keyed on the calling `YandexMusicClient` method, so a future `asyncio.gather` over the same method cannot re-introduce the burst pattern. Per-kind throttler continues to cap sustained RPS; the lock caps in-flight requests to ≤1 per endpoint family. Distinct methods still run concurrently subject only to the throttler. Cost is zero in steady-state — only matters when something fans out.

### Changed

- Reshape the seasonal-mix recommendation fallback: try the current season's tag, fall back to `autumn` only if the first call returns zero playlists. Previously a separate runtime validation call was made first; the new path makes at most one extra request when actually needed.
- Forensic logging of every 429-classified response (`markers_matched` + first 2000 chars of body) and per-request `caller=`/`kind=` diagnostic remain in the code at DEBUG level so a single captcha trip can be reconstructed by flipping the provider log level — no impact on steady-state logs.

## [3.5.14] - 2026-05-27

### Changed

- Enable stale-while-revalidate (`allow_expired_cache=True`) on every `@use_cache` method in the provider. Browse, library, search, recommendations, artist/album/track detail, and rotor wave-mode lookups now return the cached result immediately even when expired, and refresh in the background — so navigation stays snappy on slow networks or during a rate-limit cooldown. Restores the upstream Music Assistant convention that was lost during the sync of earlier releases.

## [3.5.13] - 2026-05-27

### Fixed

- Detect Russian-language bios correctly when the text has leading or trailing whitespace — padding no longer dilutes the Cyrillic-share check below threshold.
- Rank unknown-bitrate audio variants unambiguously when "efficient" quality is selected — lossless streams (reported as bitrate 0) and unknown-bitrate streams now both rank last so they never out-rank a real low-bitrate AAC.

### Changed

- Drop the unused `limit` argument from the internal Yandex search API call. Callers slice each result bucket to their requested size after classification; the lower-level call never honoured a per-type cap.
- Tighten the return-type annotation of the internal "URL refresh on 4xx" helper to reflect actual behaviour: it always returns `bytes` (empty for raw streams) or raises `MediaNotFoundError`.
- Use a defensive `getattr` for the Yandex client `base_url` attribute in the landing-blocks endpoint, mirroring the rotor-session helper. A library rename will degrade gracefully instead of raising `AttributeError`.
- Introduce `CONF_SESSION_ID` constant for the session-id config key used by both auth flows, replacing two bare string literals.
- Apply `Final` annotations uniformly to module-level constants for stricter type-checking.

### Removed

- Unused legacy auth-flow constants (`CONF_ACTION_AUTH`, `LABEL_TOKEN`, `LABEL_AUTH_INSTRUCTIONS`) and the unused `IMAGE_SIZE_SMALL` image-size constant.

## [3.5.12] - 2026-05-27

### Changed

- Improve test coverage for stream-details resolution, podcast / audiobook / episode parsers, and the recommendations orchestrator. Closes coverage gaps flagged by the codebase review: `get_stream_details` now has happy-path, download-info-fallback, and both-fail tests; the `description_language is None` invariant is regression-guarded on podcast / audiobook / episode parsers; and the My Wave recommendations folder is end-to-end tested against the real `parse_track` path so a parser/orchestrator integration regression cannot slip through.

## [3.5.11] - 2026-05-27

### Fixed

- Reduce search-result staleness from 14 days to 1 day so newly released albums appear within a day of being added to Yandex's catalogue.
- Stop discarding already-fetched playlist tracks when a single batch mid-load returns empty. The playlist now loads partially and a warning is logged; the existing all-batches-empty guard still raises terminal failures.
- Surface 4xx responses from search, liked-tracks, and liked-albums correctly. Previously these were wrapped as transient errors and Music Assistant retried in a loop reproducing the same failure; now they resolve to empty results.
- Distinguish transient network failures from invalid credentials in token validation. Good tokens are no longer dropped on a network hiccup; only Passport's terminal rejection clears them.
- Sort liked tracks safely when the upstream library returns timezone-naive timestamps for some entries and timezone-aware for others — the whole liked-tracks collection could previously fail to load with a `TypeError`.
- Apply rate-limit throttling consistently on the reconnect-retry path. Skipping the throttler acquire on the retry attempt doubled the effective request rate during connection flap, increasing Yandex smart-captcha trip risk.
- Skip the unnecessary reconnect cycle on 4xx errors. `BadRequestError` is a terminal client error from Yandex; it no longer triggers a connection reset and retry.
- Clear all per-session caches (My Wave state, wave background colors, liked-albums cache) on provider reload so stale `asyncio.Lock` objects bound to the previous event loop cannot survive a settings change.

## [3.5.10] - 2026-05-27

### Fixed

- Stop including upstream library exception detail in user-facing authentication errors. Yandex Passport failures (login, token refresh, credential refresh) now surface only the error class name, so token fragments or response bodies that the library may embed in its exception messages can no longer reach Music Assistant logs or the frontend.
- Stop embedding the signed CDN URL in stream-fetch error messages. When a Yandex audio request fails with an HTTP error, the resulting `MediaNotFoundError` now reports only the HTTP status — the URL's expiring signature no longer leaks into logs.

## [3.5.9] - 2026-05-27

### Changed

- Limit `description_language` tagging to artist biographies only. The previous release also tagged playlist / podcast / podcast-episode / audiobook descriptions, but Music Assistant currently has no metadata-provider competition for those text fields, so the language hint never affected what users see. The artist case — where multiple sources (Yandex, TheAudioDB, fanart, lastfm) compete and the user's preferred-language setting actually drives the merge — is preserved.

## [3.5.6] - 2026-05-26

### Added

- Tag Russian-language descriptions (artist bios, playlists, podcasts, episodes, audiobooks) with the new upstream `description_language` field so Music Assistant keeps the Yandex copy for Russian-speaking users instead of falling back to a metadata-provider bio in another language. Detection is based on Cyrillic script dominance; non-Russian or ambiguous text is left unset.

## [3.5.5] - 2026-05-26

### Fixed

- Reduce smart-captcha rate-limit lockouts during initial library sync: the first captcha trip now uses a 60-second cooldown that escalates only on repeated trips inside the same hour (60s → 300s → 600s). Previously a single captcha event blocked the provider for a full 10 minutes.
- Isolate artist and album metadata refresh from the rest of the API so a hot metadata burst no longer blocks search, playlists, or playback.
- Add a small jitter to API calls during the first minute after connect to smooth out the parallel metadata-refresh burst Music Assistant triggers immediately after a fresh install.
- Lower the default per-second request budget so initial library sync is less likely to trip Yandex's smart-captcha edge in the first place.
- Refresh parser test snapshots for new upstream `music_assistant_models` fields (`description_language`, `proxy_id` on images) so CI passes without behavioral changes.

## [3.4.2] - 2026-05-09

- fix(parsers): widen `Audiobook.authors` type annotation to `UniqueList[str | Artist]` to match upstream `music_assistant_models` and unblock mypy under upstream-synced typing rules.
- fix(tests/snapshots): refresh `test_parsers.ambr` for the upstream `music_assistant_models` evolution — `Artist.artist_type` (new field, default `singer`) and the new `MediaItemMetadata` fields (`review`, `mood`, `style`, `lyrics`, `lrc_lyrics`, `performers`, `preview`, `popularity`, `release_date`).
- chore: sync workflow wrappers from ma-provider-tools (CLAUDE.md, ruff/mypy/codespell from upstream music-assistant/server, config-sync CI guard).

## [3.3.0] - 2026-04-23

- feat(audiobook): sync progress to Yandex, surface in search and browse (#115) (`0e9cda6`)
- chore: update changelog for v3.2.1 [skip ci] (`2bbc168`)

---

## [3.3.1] - 2026-04-23

- fix(search): apply limit per bucket after classify_album (#116) (`272461a`)
- chore: update changelog for v3.3.0 [skip ci] (`ec79132`)

---

## [3.4.0] - 2026-04-23

- feat(rotor): migrate My Wave to session API + wave modes, presets, prefetch (#118) (`529b686`)
- chore(changelog): remove duplicate 3.3.0 and 3.3.1 entries (#117) (`7a89c08`)
- chore: update changelog for v3.3.1 [skip ci] (`8d73362`)

---

## [3.4.1] - 2026-04-23

- fix(rotor): surface UnauthorizedError on /rotor/session/* as LoginFailed (#120) (`c08adfa`)
- fix(presets): drop whitespace-only dropdown values + strip surrounding spaces (#119) (`d375a0d`)
- chore: update changelog for v3.4.0 [skip ci] (`41f2932`)

---

## [3.4.2] - 2026-05-09

- chore: sync workflow wrappers from ma-provider-tools (#130) (`a0938ab`)
- chore: sync workflow wrappers from ma-provider-tools (#127) (`5917238`)
- chore: sync workflow wrappers from ma-provider-tools (#125) (`bd264b8`)
- chore: sync workflow wrappers from ma-provider-tools (#123) (`9ec09c5`)
- chore: update changelog for v3.4.1 [skip ci] (`9357d95`)

---

## [3.5.1] - 2026-05-12

- chore: bump VERSION to 3.5.1 (`dbbc460`)
- chore: update changelog for v3.5.0 [skip ci] (`e447034`)
- style: auto-fix ruff (`2ea0a1b`)

---

## [3.5.4] - 2026-05-13

- fix(rate-limit): cooldown re-check on retry + cache awareness during cooldown (`759791c`)
- style: auto-fix ruff (`a198cb9`)

---

## [3.5.7] - 2026-05-26

- style: auto-fix ruff (`c8f9abd`)

---

## [3.5.8] - 2026-05-26

- chore: update changelog for v3.5.7 [skip ci] (`69f4cdf`)

---

## [3.5.11] - 2026-05-27

- fix(resilience): distinguish transient from terminal errors across the stack (#158) (`1901fbf`)
- style: auto-fix ruff (`fd1ad0b`)

---

## [3.5.12] - 2026-05-27

- test: close coverage gaps in stream-details, parsers, and recommendations (#160) (`f4c73f3`)
- chore: update changelog for v3.5.11 [skip ci] (`bd7be94`)

---

## [3.5.13] - 2026-05-27

- chore(modules): hygiene pass — Final annotations, dead constants, idioms (#162) (`a8905ed`)
- chore: update changelog for v3.5.12 [skip ci] (`0615505`)

---

<!-- changelog entries will be added here by release workflow -->

## [3.5.0] - 2026-05-12

- feat(rate-limit): captcha-aware retry, per-kind throttling, file-info cache (#140) (`d821cb3`)
- chore: sync workflow wrappers from ma-provider-tools (#139) (`bf8b6be`)
- chore: sync workflow wrappers from ma-provider-tools (#138) (`6af7612`)
- chore: sync workflow wrappers from ma-provider-tools (#137) (`b1cacca`)
- chore: sync workflow wrappers from ma-provider-tools (#136) (`67d7bc6`)
- chore: sync workflow wrappers from ma-provider-tools (#135) (`c3e17a0`)
- chore: sync workflow wrappers from ma-provider-tools (#134) (`fdc4b91`)
- chore: sync workflow wrappers from ma-provider-tools (#132) (`bf27ce9`)
- chore: update changelog for v3.4.2 [skip ci] (`974c6c7`)

---

## [3.2.1] - 2026-04-22

- fix(audiobook): wire seek through can_seek and bound chapter failures (`40bdc9b`)
- chore: update changelog for v3.2.0 [skip ci] (`f499ea4`)

---

## [3.2.0] - 2026-04-21

- feat(audiobook): stream audiobooks via chapter concatenation (`d9f483c`)
- chore: update changelog for v3.1.2 [skip ci] (`d10fffb`)

---

## [3.1.2] - 2026-04-21

- fix(auth): clear stale refresh_token on QR re-auth (`48d50c4`)
- chore: update changelog for v3.1.1 [skip ci] (`4809461`)

---

## [3.1.1] - 2026-04-21

- chore: bump version to 3.1.1 (`917f43e`)
- fix(auth): wrap transient Passport errors in _reauth_via_refresh_token (`5ad9fff`)
- chore: expand changelog for v3.1.0 [skip ci] (`55da091`)
- chore: update changelog for v3.1.0 [skip ci] (`0f91ad1`)

---

## [3.1.0] - 2026-04-21

- feat(library): podcasts + audiobook classifier (Phase 1) — liked albums routed to music/podcast/audiobook views via `meta_type`/`type`; podcasts fully wired (list, detail, episodes, like/unlike, search, stream); audiobook chapters from `album.volumes`; audiobook streaming raises `NotImplementedError` pending Phase 2 (#112) (`e0c27c9`)
- feat(library): short-lived `_get_liked_albums_cached` (30s, asyncio.Lock) dedupes the three library syncs into one API call per cycle (#112) (`e0c27c9`)
- fix(classify): audiobooks in production are `meta_type=podcast` + `type=audiobook` — "audiobook" now wins over "podcast" on any field (#112) (`e0c27c9`)
- fix(parsers): copy parent podcast images into episode instead of sharing the mutable `UniqueList` reference (#112) (`e0c27c9`)
- fix(podcast): `get_podcast_episode` raises `InvalidDataError` when parent album is missing — no `item_id="unknown"` fallback (#112) (`e0c27c9`)
- fix(features): restore `ProviderFeature.SIMILAR_ARTISTS` (regression from Phase 1 rebase) (#112) (`e0c27c9`)
- fix(quality): normalize legacy 'lossless' to QUALITY_SUPERB in get_quality (`935a518`)
- fix(auth): don't clear creds on transient Passport failures (`31abe95`)

---

## [3.0.1] - 2026-04-20

- Update VERSION (`dc9c2bb`)
- fix: address PR review comments (`41d1709`)
- fix: address PR review comments (`bad8a70`)
- test: remove integration test module (`7d82a5a`)
- fix(manifest): drop [async] extra from yandex-music requirement (`853fa42`)
- fix(device-auth): don't log user_code at INFO level (`24b211c`)
- chore: clean up CHANGELOG — order, dedup, noise [skip ci] (`50bc67e`)
- Bump version from 2.9.1 to 3.0.0 (`278b2b8`)
- chore: update changelog for v3.0.0 [skip ci] (`fe1de36`)

---

## [3.0.0] - 2026-04-19

- feat: migrate to yandex-music v3 + Pinned/History browse + Device Flow auth (#102) (`5d4a54f`)
- refactor: merge device_auth + yandex_auth into single auth module (#109) (`5bcaa16`)
- fix(streaming): accept camelCase downloadInfo from yandex-music v3 (#106) (`f29fe2e`)
- fix(streaming): restrict can_seek to byte-seekable codecs (`07001a5`)
- fix(device-auth): show user code in MA-served intermediate page (#104) (`bacaec2`)
- fix(device-auth): readable popup + auto-close after authorization (#107) (`b54f6ea`)

---

## [2.9.1] - 2026-04-16

- feat(streaming): native seek support for raw transport (#88) (`afc589a`)
- feat: add get_rotor_station_tracks and get_quality wrapper methods (`b84630b`)
- fix(streaming): only set can_seek when byte offset is computable (`b24cadb`)
- fix: re-raise CancelledError in get_track_file_info, fix docstring (`d04d453`)
- fix(ci): add runtime deps to pyproject.toml for test discovery (`cf6424f`)
- fix(dev): use unsafe-best-match index strategy for dev deps (`6d5bccd`)
- fix: make CONF_TOKEN required to prevent saving without auth (`acc0c5e`)
- fix: raise InvalidDataError for missing session_id in QR auth (`a331238`)
- fix: pin ya-passport-auth==1.0.0 in manifest.json (`6af4819`)
- chore: bump ya-passport-auth to 1.2.3 (`2865bd8`)
- chore: update Python version in mypy configuration (`044407a`)

---

## [2.9.0] - 2026-04-10

- feat: replace manual QR auth with ya-passport-auth library (#85) (`8529ce2`)
- chore: switch ya-passport-auth to stable PyPI release (#87) (`5e3824d`)
- fix: handle ValueError in hex key decoding and TimeoutError in auth (`900c8a1`)
- fix: correct MP4 sample_rate offset and re-raise CancelledError in probe (`fcde68c`)
- fix: update stream detail assertions to match CUSTOM stream type (`dd245e4`)
- fix: mock get_track_file_info in integration tests to prevent coroutine error (`4e49fd0`)

---

## [2.8.0] - 2026-04-09

- refactor: unify streaming under get-file-info with raw transport (#71) (`a89972b`)
- fix: read bitrate from API and use lossless quality for MP3 320 (`b5f6a24`)
- fix: parse real audio params from API and container headers (`6f45425`)
- fix: auto-parse codec strings so content_type reflects audio codec, not container (`27b830a`)
- fix: make CONF_TOKEN required to prevent saving without credentials (`95118d3`)
- fix: use or-operator instead of ternary for FURB110 lint rule (`5ba024e`)
- fix: address Copilot review feedback on QR auth PR (`09dda3b`)

---

## [2.7.2] - 2026-04-07

- fix: try multiple CSRF token extraction patterns for Yandex Passport (`f6f7817`)

---

## [2.7.1] - 2026-04-07

- fix: add mobile User-Agent to QR auth requests (`57ac5b8`)

---

## [2.7.0] - 2026-04-07

- feat: QR-code authentication as primary login method (#68) (`60140d6`)
- fix: update playlist snapshots for MA models 1.1.110 (is_dynamic field) (`fc2c0d1`)
- fix: use received HTTP bytes (not decrypted) for EOF detection in windowed stream (`a038107`)
- fix: detect EOF at exact _RANGE_WINDOW boundary via Content-Range header (`fd3e26f`)
- refactor: extract _handle_stream_error to fix PLR0915 in get_audio_stream (`9bbdc8e`)
- chore: improve manifest description and add credits field (`c396505`)

---

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
