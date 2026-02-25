---
title: Docker
---

# Yandex Music — локальная разработка через Docker

Запусти полноценный Music Assistant с провайдером Yandex Music одной командой —
без установки Python, FFmpeg и прочих зависимостей.

## Требования

- [Docker](https://docs.docker.com/get-docker/)

## Быстрый старт

```bash
docker compose -f docker-compose.dev.yml up
```

Открой **http://localhost:8095** в браузере.

## Первый запуск: создание пользователя

При первом старте MA запускает мастер настройки:

1. **Создай пользователя** — задай логин и пароль (хранится в `.ma-data/` локально)
2. Пропусти интеграцию с Home Assistant, если предложат
3. Данные входа сохраняются между перезапусками контейнера через том `.ma-data/`

## Подключение провайдера Yandex Music

После входа:

1. Перейди в **Settings** → **Providers**
2. Найди **Yandex Music** в списке — он уже доступен, код загружен автоматически
3. Нажми **Add** и введи свои учётные данные
4. Конфигурация провайдера сохраняется в `.ma-data/` и переживает перезапуски

> 💡 Если провайдер не появляется — проверь логи (`docker compose -f docker-compose.dev.yml logs`).
> Ошибка при старте будет видна там.

## Управление контейнером

| Действие | Команда |
|----------|---------|
| Запустить | `docker compose -f docker-compose.dev.yml up` |
| Запустить в фоне | `docker compose -f docker-compose.dev.yml up -d` |
| Остановить | `docker compose -f docker-compose.dev.yml down` |
| Перезапустить | `docker compose -f docker-compose.dev.yml restart` |
| Логи | `docker compose -f docker-compose.dev.yml logs -f` |
| Сбросить состояние | `rm -rf .ma-data/` → запустить заново |

## Изменения в коде провайдера

Код из `provider/` смонтирован в контейнер через симлинк.
Изменения подхватываются после перезапуска контейнера — пересборка образа не нужна:

```bash
docker compose -f docker-compose.dev.yml restart
```

## Сохранение состояния

Весь конфиг MA, учётные данные провайдера и кеш хранятся в `.ma-data/` (добавь в `.gitignore`).
Папка создаётся автоматически при первом запуске.
