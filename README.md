# Провайдер Яндекс Музыки для Music Assistant

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

Подходы к работе с ротором и динамическими плейлистами подсмотрены в нескольких сторонних реализациях — в первую очередь за переход на session-based API (`/rotor/session/*` с долгоживущим `radioSessionId`), формат сидов пресетов (`settingDiversity:*`, `settingMoodEnergy:*`, `settingLanguage:*`) и схему событий обратной связи.

| Проект | Язык | Что подсмотрено |
|--------|------|------------------|
| [MarshalX/yandex-music-api](https://github.com/MarshalX/yandex-music-api) | Python | Базовый SDK (уже используется как зависимость); формы запросов ротора и feedback-shortcuts |
| [chernyshalexander/YandexMusicLMS](https://github.com/chernyshalexander/YandexMusicLMS/tree/experiment) | Perl | Session-API `/rotor/session/{new,tracks,feedback}`, набор wave-режимов (Discover / Calm / Active / …) и presets-UX |
| [DECE2183/yamusic-tui](https://github.com/DECE2183/yamusic-tui) | Go | Семантика `queue = первый трек предыдущего батча`, порядок событий feedback перед запросом следующего батча |
| [music-assistant/server](https://github.com/music-assistant/server) | Python | Контракты провайдера (`get_similar_tracks`, `recommendations`, `is_dynamic`); правила поведения с очередью — провайдер не трогает DSTM за пользователя |

## Благодарности

- [@peholod009](https://github.com/peholod009) — за помощь в тестировании и обратную связь
- [@alkmarmasor](https://github.com/alkmarmasor) — за идеи и наработки в форке провайдера

## Лицензия

[Apache 2.0](LICENSE) — история изменений в [CHANGELOG.md](CHANGELOG.md).
