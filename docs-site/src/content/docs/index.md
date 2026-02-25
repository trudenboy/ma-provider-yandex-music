---
title: Провайдер Yandex Music
description: Документация провайдера Yandex Music для Music Assistant
---

<img src="https://raw.githubusercontent.com/trudenboy/ma-provider-yandex-music/dev/provider/icon.svg" alt="Yandex Music" style="width: 72px; float: right; margin: 0 0 1rem 1.5rem;" />


Music Assistant поддерживает [Yandex Music](https://music.yandex.ru) — музыкальный стриминговый сервис.
Провайдер создан и поддерживается [TrudenBoy](https://github.com/TrudenBoy).

Реализован на основе библиотеки [yandex-music](https://github.com/MarshalX/yandex-music-api) (неофициальный клиент Yandex Music API).

:::caution[Дисклеймер]
Это неофициальная реализация, не связанная с компанией Яндекс и не одобренная ею. Используйте на свой страх и риск.
:::



## Возможности


| Функция | Поддержка |
|:--------|:---------:|
| Исполнители, Альбомы, Треки, Плейлисты | ✅ |
| Поиск по каталогу | ✅ |
| Синхронизация библиотеки (двунаправленная) | ✅ |
| [Рекомендации на главном экране](features/recommendations/) | ✅ |
| [Моя волна / Radio Mode](features/my-wave/) | ✅ |
| [Радиостанции / Rotor](features/radio/) | ✅ |
| [Похожие треки](features/similar-tracks/) | ✅ |
| [Тексты песен](features/lyrics/) | ✅ |
| [Подборки и миксы](features/picks-and-mixes/) | ✅ |
| [Просмотр каталога (Browse)](features/browse/) | ✅ |
| [Качество звука до Lossless FLAC](features/audio-quality/) | ✅ |
| Несколько аккаунтов одновременно | ✅ |
| Максимальное качество | Lossless FLAC (с подпиской Яндекс Плюс) |
| Способ входа | OAuth-токен |



## Настройка


Инструкция по подключению — на странице [Настройка](configuration/).



## Известные проблемы


Полный список — на странице [Известные проблемы](known-issues/).
