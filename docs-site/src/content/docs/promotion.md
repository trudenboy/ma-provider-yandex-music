---
title: Продвижение и SEO
description: Как настроить визуальную презентацию и SEO для репозитория Yandex Music
---

Этот документ описывает, как поддерживается визуальное представление репозитория **Yandex Music** на GitHub и в поиске.

## Что синхронизируется автоматически

Через `ma-provider-tools` распространяются и поддерживаются:

- **`About`-блок** (`description`, `homepage`, `topics`) — задаются в `providers.yml` (поля `github_description`, `github_topics`, `github_homepage`) и применяются скриптом `scripts/sync_repo_settings.py` + workflow `sync-repo-settings.yml`.
- **README-шапка** — блок между маркерами `<!-- >>> ma-provider-tools sync (readme header) >>> -->` и `<!-- <<< ma-provider-tools sync (readme header) <<< -->`. Содержит badges (CI / Release / License / Music Assistant / Stars), быстрые ссылки и cross-link на родственные провайдеры.
- **Стартовая страница docs-site** (этот сайт) — hero-блок берёт `github_description`, под ним ряд тегов из `github_topics` и тот же ряд badges, что в README.

Локальные правки этих блоков **не сохраняются**: следующий запуск `distribute.yml` перезапишет их. Чтобы изменить описание или topics — открывайте PR в `ma-provider-tools`.

## Social preview (превью при шаринге ссылки)

GitHub API **не поддерживает** загрузку изображения превью — это делается только вручную через UI. Рекомендуется:

1. PNG 1280×640 пикселей.
2. Visual: иконка/логотип провайдера + название + 1-2 ключевые фразы.
3. Загрузить через: **Repo Settings → Social preview → Edit**.

Это P1-задача — автогенерация через GitHub Action рассматривается отдельно.
