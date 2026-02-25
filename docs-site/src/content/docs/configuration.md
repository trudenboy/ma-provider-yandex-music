---
title: Настройка
---

## Получение токена

Провайдер использует **X-Auth-Token** для авторизации в Yandex Music.

### Способ 1: Автоматически (рекомендуется)

Используй утилиту [yandex-music-token](https://github.com/MarshalX/yandex-music-token):

```bash
pip install yandex-music-token
python -m yandex_music_token
```

Следуй инструкциям — введи логин/пароль или войди через браузер. Токен будет выведен в терминал.

### Способ 2: Из браузера

1. Открой [music.yandex.ru](https://music.yandex.ru) и войди в аккаунт
2. Открой DevTools → Application → Cookies
3. Найди cookie `Session_id` или перехвати запрос с заголовком `X-Yandex-Music-Client`
4. Воспользуйся расширением [Yandex Music Token](https://github.com/MarshalX/yandex-music-token/releases) для браузера

## Добавление провайдера в Music Assistant

1. Открой **Music Assistant → Настройки → Провайдеры**
2. Нажми **Добавить провайдер** и выбери **Yandex Music**
3. Вставь токен в поле **X-Auth-Token**
4. Нажми **Сохранить**

## Параметры

| Параметр | Описание | По умолчанию |
|:---------|:---------|:-------------|
| X-Auth-Token | Токен авторизации Yandex Music | — |
| Качество | Максимальное качество потока | Auto |
