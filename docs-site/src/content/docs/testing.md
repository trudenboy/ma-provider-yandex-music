---
title: Тестирование
---


## Быстрый старт

```bash
uv run pytest provider/tests/ -v
```

С отчётом о покрытии:

```bash
uv run pytest provider/tests/ -v --cov=provider/ --cov-report=term-missing
```

## CI-пайплайн

Каждый push и PR запускают два параллельных задания через `test.yml`:

| Задание | Что делает |
|---------|-----------|
| `test-*` | Запускает pytest с проверкой покрытия, загружает отчёт в Codecov |
| `lint-*` | Запускает ruff, mypy, codespell, pre-commit |


Тесты запускаются на основе `music-assistant/server@dev` (без форка — лёгкий CI).

## Инструменты

| Инструмент | Назначение |
|-----------|-----------|
| `uv` | Управление виртуальным окружением и зависимостями |
| `Python 3.12` | Целевая версия языка |
| `pytest` | Фреймворк для тестов |
| `pytest-cov` | Сбор данных о покрытии |
| `Codecov` | Загрузка отчётов о покрытии (автоматически в CI) |
| `ruff` | Линтер и форматтер Python |
| `mypy` | Статический анализ типов |
| `codespell` | Проверка орфографии в исходном коде |
| `pre-commit` | Хуки для проверки перед коммитом |

## Запуск линтеров локально

Запустить все хуки pre-commit (рекомендуется перед PR):

```bash
uv run pre-commit run --all-files
```

Только проверка типов:

```bash
uv run mypy provider/
```

Только линтинг:

```bash
uv run ruff check provider/
uv run ruff format --check provider/
```

## Покрытие

Отчёты о покрытии автоматически загружаются в Codecov при каждом push в CI.
Локально просмотреть покрытие:

```bash
uv run pytest provider/tests/ --cov=provider/ --cov-report=html
open htmlcov/index.html
```

## Если CI упал

Если тесты или линтеры упали в CI, автоматически создаётся GitHub-задача с меткой `incident:ci`.
Подробнее о процессе работы с инцидентами: [Управление инцидентами](incident-management.md).
