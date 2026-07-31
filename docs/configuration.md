=== "English"

    # Configuration

    Provider settings are available via **Settings → Music Sources → Yandex Music**.
    New instances use Music Assistant's guided setup flow.

    ### Authentication

    Choose one of three login methods when adding or reconfiguring the provider:

    | Method | Description |
    |--------|-------------|
    | **QR code** (default) | Scan the high-contrast QR code with the Yandex app and confirm the login. |
    | **Device code** | Open the address shown in the yellow card, then enter the large code on that page. |
    | **Token (manual)** | Paste an existing Yandex Music token. The token is validated before the provider is saved, but cannot refresh automatically. |

    Expired QR and Device codes are renewed automatically. The complete interactive login
    stops after 15 minutes; start **Reconfigure** to try again.

    **Remember session** applies to QR and Device Code login and is enabled by default.
    When enabled, the provider stores the long-lived session credentials needed to refresh
    an expired music token. When disabled, only the current music token is stored and you
    must reauthenticate after it expires. Manual-token login always stores only that token.

    ### Reauthenticate or replace a token

    To restart QR, Device Code, or manual-token login for an existing instance, open the
    provider menu and select **Reconfigure**. You do not need to delete and recreate the
    provider.

    Advanced settings also contain **Replace Yandex Music token**, a one-shot field for
    changing only the token. Leave it empty to keep the current credentials. When saved,
    the replacement is validated and moved to protected setup storage; the field is then
    cleared. An invalid replacement is discarded without overwriting the working stored
    credentials.

    ### Obtaining a token for manual login

    Manual login is optional. If you already use QR or Device Code, no token needs to be
    copied manually.

    1. Open [Yandex OAuth](https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d).
    2. Sign in and allow access when prompted.
    3. Copy the value after `access_token=` and before the next `&` in the redirected URL.
    4. Select **Token (manual)** in guided setup and paste the value.

    ### Settings

    **Basic settings:**

    | Setting | Default | Description |
    |---------|---------|-------------|
    | **Audio quality** | Balanced | Choose Efficient, Balanced, High, or Superb quality. |

    **Advanced settings** (select **Show advanced settings**):

    | Setting | Default | Description |
    |---------|---------|-------------|
    | **My Wave maximum tracks** | 150 | Tracks exposed by the My Wave playlist; allowed range is 10–1000. |
    | **My Wave presets** | None | Build named presets from optional diversity, mood, and language filters; saved presets appear under **Radio → My Presets**. |
    | **Liked Tracks maximum tracks** | 200 | Tracks exposed by the Liked Tracks virtual playlist; allowed range is 50–2000. Higher values increase loading time and CAPTCHA risk. |
    | **API Base URL** | `https://api.music.yandex.net` | Change only if Yandex changes its API endpoint. |
    | **Restrictive rate limits** | Off | Safer request concurrency for VPS, VPN, and datacenter IPs; residential users normally leave this disabled. |
    | **Replace Yandex Music token** | Empty | Optional one-shot token replacement described above. |

    ### Quality options

    | Value | Label | Format | Bitrate |
    |-------|-------|--------|---------|
    | `efficient` | Efficient | AAC | ~64 kbps |
    | `balanced` | Balanced | AAC | ~192 kbps |
    | `high` | High | MP3 | ~320 kbps |
    | `superb` | Superb | FLAC | Lossless |

=== "Русский"

    # Настройка

    Параметры провайдера доступны через **Настройки → Музыкальные источники → Яндекс Музыка**.
    Новые экземпляры подключаются через пошаговую настройку Music Assistant.

    ### Авторизация

    При добавлении или повторной настройке провайдера выберите один из трёх способов:

    | Способ | Описание |
    |--------|----------|
    | **QR-код** (по умолчанию) | Отсканируйте контрастный QR-код приложением Яндекса и подтвердите вход. |
    | **Device Code** | Откройте адрес из жёлтой карточки и введите на этой странице крупный код. |
    | **Токен (вручную)** | Вставьте существующий токен Яндекс Музыки. Перед сохранением он проверяется, но не может обновляться автоматически. |

    Просроченные QR- и Device-коды обновляются автоматически. Весь интерактивный процесс
    завершается через 15 минут; для новой попытки запустите **Reconfigure**.

    **Remember session** применяется к QR и Device Code и по умолчанию включён.
    В этом режиме провайдер хранит долгоживущие данные сессии, необходимые для обновления
    истёкшего музыкального токена. Если выключить параметр, сохранится только текущий
    музыкальный токен и после его истечения потребуется повторная авторизация. При ручном
    входе всегда сохраняется только введённый токен.

    ### Повторная авторизация или замена токена

    Чтобы заново запустить QR, Device Code или ручной вход для существующего экземпляра,
    откройте меню провайдера и выберите **Reconfigure**. Удалять и создавать провайдер заново
    не требуется.

    В расширенных настройках также есть одноразовое поле **Replace Yandex Music token**.
    Оставьте его пустым, чтобы сохранить текущие данные. После сохранения новый токен
    проверяется, переносится в защищённое хранилище настройки и удаляется из поля. Неверный
    токен отбрасывается, не перезаписывая рабочие сохранённые данные.

    ### Получение токена для ручного входа

    Ручной вход необязателен. При использовании QR или Device Code самостоятельно копировать
    токен не нужно.

    1. Откройте [Yandex OAuth](https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d).
    2. Войдите и разрешите доступ, если появится запрос.
    3. В адресе после перенаправления скопируйте значение между `access_token=` и следующим `&`.
    4. Выберите **Токен (вручную)** в пошаговой настройке и вставьте значение.

    ### Параметры

    **Основные параметры:**

    | Параметр | По умолчанию | Описание |
    |----------|--------------|----------|
    | **Audio quality** | Balanced | Выбор качества Efficient, Balanced, High или Superb. |

    **Расширенные параметры** (выберите **Show advanced settings**):

    | Параметр | По умолчанию | Описание |
    |----------|--------------|----------|
    | **My Wave maximum tracks** | 150 | Число треков в плейлисте «Моя волна»; допустимый диапазон — 10–1000. |
    | **My Wave presets** | Нет | Создание именных пресетов из необязательных фильтров разнообразия, настроения и языка; сохранённые пресеты доступны в **Радио → Мои пресеты**. |
    | **Liked Tracks maximum tracks** | 200 | Число треков в виртуальном плейлисте «Понравившиеся»; допустимый диапазон — 50–2000. Большие значения увеличивают время загрузки и риск CAPTCHA. |
    | **API Base URL** | `https://api.music.yandex.net` | Менять только при изменении адреса API Яндексом. |
    | **Restrictive rate limits** | Выключено | Более безопасное ограничение запросов для VPS, VPN и адресов дата-центров; домашним пользователям обычно не требуется. |
    | **Replace Yandex Music token** | Пусто | Необязательная одноразовая замена токена, описанная выше. |

    ### Варианты качества

    | Значение | Название | Формат | Битрейт |
    |----------|----------|--------|---------|
    | `efficient` | Efficient | AAC | ~64 кбит/с |
    | `balanced` | Balanced | AAC | ~192 кбит/с |
    | `high` | High | MP3 | ~320 кбит/с |
    | `superb` | Superb | FLAC | Без потерь |
