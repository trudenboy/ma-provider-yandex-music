# Провайдер Яндекс Музыки для Music Assistant


<!-- >>> ma-provider-tools sync (readme header) — DO NOT EDIT >>> -->
[![CI](https://github.com/trudenboy/ma-provider-yandex-music/actions/workflows/test.yml/badge.svg)](https://github.com/trudenboy/ma-provider-yandex-music/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/trudenboy/ma-provider-yandex-music?display_name=tag)](https://github.com/trudenboy/ma-provider-yandex-music/releases/latest)
[![License](https://img.shields.io/github/license/trudenboy/ma-provider-yandex-music)](LICENSE)
[![Music Assistant](https://img.shields.io/endpoint?url=https%3A%2F%2Ftrudenboy.github.io%2Fma-provider-tools%2Fbadges%2Fyandex_music.json)](https://www.music-assistant.io/)
[![Stars](https://img.shields.io/github/stars/trudenboy/ma-provider-yandex-music?style=flat&logo=github)](https://github.com/trudenboy/ma-provider-yandex-music/stargazers)

**📖 [Documentation / Документация](https://trudenboy.github.io/ma-provider-yandex-music/)** · **🔄 [Changelog / Журнал](CHANGELOG.md)** · **🐛 [Issues / Проблемы](https://github.com/trudenboy/ma-provider-yandex-music/issues)** · **💬 [Discussions / Обсуждения](https://github.com/trudenboy/ma-provider-yandex-music/discussions)**

**Related providers:** [Yandex Music Connect (Ynison)](https://github.com/trudenboy/ma-provider-yandex-ynison)
<!-- <<< ma-provider-tools sync (readme header) <<< -->

[English](README.en.md) | Русский

📖 <a href="https://trudenboy.github.io/ma-provider-yandex-music/">Документация пользователя</a>


> Слушайте свою библиотеку [Яндекс Музыки](https://music.yandex.ru/) через [Music Assistant](https://music-assistant.io/) с полной поддержкой навигации, поиска, радио и воспроизведения без потерь.

## Быстрый старт (Docker)

```bash
# Клонируйте репозиторий
git clone https://github.com/trudenboy/ma-provider-yandex-music.git
cd ma-provider-yandex-music

# Запустите Music Assistant с предустановленным провайдером
docker compose -f docker-compose.dev.yml up
```

Откройте веб-интерфейс MA по адресу `http://localhost:8095`, затем перейдите в **Настройки → Музыкальные источники → Добавить источник → Яндекс Музыка** и введите ваш OAuth-токен.

Подробное руководство по Docker-окружению для разработки: [docs/dev-docker.md](docs/dev-docker.md).

## Возможности

- **Синхронизация библиотеки** — Исполнители, Альбомы, Треки (Понравившиеся), Плейлисты синхронизируются с библиотекой MA
- **Редактирование библиотеки** — Лайк / дизлайк Исполнителей, Альбомов, Треков прямо из MA
- **Навигация** — Понравившиеся треки, Радио «Моя волна», Подборки и Миксы (настроение/эпоха/активность/жанр), Лента, Чарт, Исполнители, Альбомы, Плейлисты
- **Рекомендации** — персональные разделы «Для вас», представленные как папки рекомендаций MA
- **Поиск** — Треки, Исполнители, Альбомы, Плейлисты
- **Похожие треки** — на основе станции ротора Яндекса
- **Тексты песен** — получаются через API Яндекс Музыки
- **Качество звука** — Экономичное (AAC ~64 кбит/с) / Сбалансированное (AAC ~192 кбит/с) / Высокое (MP3 ~320 кбит/с) / Превосходное (FLAC без потерь, с AES-дешифрованием для encraw-транспорта)
- **Радио «Моя волна»** — бесконечное персональное радио с обратной связью ротора и постраничной навигацией
- **Мультиаккаунт** — одновременное подключение нескольких аккаунтов Яндекс Музыки

## Документация

| Руководство | Описание |
|-------------|----------|
| [Настройка](docs/configuration.md) | Токен, качество, «Моя волна», настройки понравившихся треков |
| [Разработка](docs/development.md) | Настройка окружения, тесты, линтинг, формат коммитов |
| [Участие в разработке](docs/contributing.md) | Сообщения об ошибках, предложения, pull request'ы |
| [Тестирование](docs/testing.md) | Запуск тестов, CI-пайплайн, покрытие |
| [Управление инцидентами](docs/incident-management.md) | Метки, автоматическое отслеживание, триаж Copilot |
| [Локальная разработка (Docker)](docs/dev-docker.md) | Запуск MA + провайдера без установки зависимостей |

## Ссылки

- [Music Assistant](https://music-assistant.io/) — open-source музыкальный сервер от Marcel van der Veldt
- [Яндекс Музыка](https://music.yandex.ru/) — стриминговый сервис от Яндекса

## Референсные проекты

- [MarshalX/yandex-music-api](https://github.com/MarshalX/yandex-music-api) — неофициальный Python-клиент Яндекс Музыки (используется как зависимость)
- [chernyshalexander/YandexMusicLMS](https://github.com/chernyshalexander/YandexMusicLMS/tree/experiment) — плагин Яндекс Музыки для Lyrion Music Server
- [DECE2183/yamusic-tui](https://github.com/DECE2183/yamusic-tui) — терминальный клиент Яндекс Музыки
- [music-assistant/server](https://github.com/music-assistant/server) — ядро Music Assistant

## Благодарности

- [@peholod009](https://github.com/peholod009) — за помощь в тестировании и обратную связь
- [@alkmarmasor](https://github.com/alkmarmasor) — за идеи и наработки в форке провайдера

## Лицензия

[Apache 2.0](LICENSE) — история изменений в [CHANGELOG.md](CHANGELOG.md).
