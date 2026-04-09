---
title: Окружение разработки
description: Настройка окружения разработки для провайдера Yandex Music
---


## Требования

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- ffmpeg 6.1+ (для интеграционных тестов MA)
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt-get install ffmpeg`
- Форк [trudenboy/ma-server](https://github.com/trudenboy/ma-server) (для dev-сервера)

## Установка

```bash
./scripts/setup.sh
```

Перезапускайте после `git pull` — версия моделей MA может измениться.

## Запуск тестов

```bash
# Unit-тесты (без MA-сервера)
uv run pytest provider/tests/ -m "not integration"

# Полный набор тестов
uv run pytest provider/tests/

# С отчётом покрытия
uv run pytest provider/tests/ --cov=provider/ --cov-report=html
```

## Именование веток

```
feature/<описание>    # новый функционал
fix/<описание>        # исправления багов
chore/<описание>      # обслуживание
```

`<описание>` — kebab-case, 2–4 слова.

## Жизненный цикл feature-ветки

```bash
git checkout dev && git pull
git checkout -b feature/my-feature

# разработка + тесты
uv run pytest provider/tests/
pre-commit run --all-files

# PR: feature/* → dev
git push origin feature/my-feature
gh pr create --base dev
```

## Запуск dev-сервера

```bash
./scripts/dev-server.sh
# UI: http://localhost:8095
```

## Conventional Commits

```
feat: add feature X
fix: fix bug Y
chore: update dependencies
test: add test for Z
```

## Процесс релиза

1. PR: `dev` → `main`
2. Actions → Release → Run workflow → ввести версию


