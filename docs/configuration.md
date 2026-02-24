=== "English"

    # Configuration

    All settings are accessible via **Settings → Music Sources → Yandex Music**.

    ### Obtaining the Token

    1. Open your browser and navigate to [Yandex OAuth](https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d)
    2. Log in with your Yandex account if prompted
    3. After authorization, you will be redirected to a URL containing `access_token=YOUR_TOKEN`
    4. Copy the token value (the part after `access_token=` and before `&`)
    5. Paste this token into the Music Assistant Yandex Music provider configuration

    ### Settings

    The provider has 7 settings. The first 3 are shown by default; the rest are under "Show advanced settings."

    **Basic settings:**

    | Setting | Default | Description |
    |---------|---------|-------------|
    | **Yandex Music Token** | — | Your OAuth token (see above). Required for authentication. |
    | **Reset authentication** | — | Clears the stored token, allowing you to re-enter credentials. |
    | **Audio quality** | Balanced | Choose between Efficient (~64 kbps AAC), Balanced (~192 kbps AAC), High (~320 kbps MP3), or Superb (Lossless FLAC). |

    **Advanced settings** (click "Show advanced settings" to see these):

    | Setting | Default | Description |
    |---------|---------|-------------|
    | **My Wave maximum tracks** | 150 | How many tracks to load for My Wave. Lower = faster loading. |
    | **Liked Tracks maximum tracks** | 500 | How many liked tracks to show. Lower = faster loading. |
    | **API Base URL** | `https://api.music.yandex.net` | Only change if Yandex changes their API endpoint. |
    | **Locale override** | — | Override the locale used for folder names (e.g. `ru_RU`). Leave blank to use Music Assistant's locale. |

    ### Quality Options

    | Value | Label | Format | Bitrate |
    |-------|-------|--------|---------|
    | `efficient` | Efficient | AAC | ~64 kbps |
    | `balanced` | Balanced | AAC | ~192 kbps |
    | `high` | High | MP3 | ~320 kbps |
    | `superb` | Superb | FLAC | Lossless |

=== "Русский"

    # Настройка

    Все настройки доступны через **Settings → Music Sources → Yandex Music**.

    ### Получение токена

    1. Откройте браузер и перейдите на страницу [Yandex OAuth](https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d)
    2. Войдите в свой аккаунт Яндекса, если потребуется
    3. После авторизации вы будете перенаправлены на URL, содержащий `access_token=ВАШ_ТОКЕН`
    4. Скопируйте значение токена (часть после `access_token=` и перед `&`)
    5. Вставьте токен в настройки провайдера Yandex Music в Music Assistant

    ### Настройки

    Провайдер имеет 7 настроек. Первые 3 отображаются по умолчанию; остальные доступны через «Show advanced settings».

    **Основные настройки:**

    | Настройка | По умолчанию | Описание |
    |-----------|-------------|----------|
    | **Yandex Music Token** | — | Ваш OAuth-токен (см. выше). Обязателен для аутентификации. |
    | **Reset authentication** | — | Сбрасывает сохранённый токен для повторной авторизации. |
    | **Audio quality** | Balanced | Выбор между Efficient (~64 кбит/с AAC), Balanced (~192 кбит/с AAC), High (~320 кбит/с MP3) или Superb (Lossless FLAC). |

    **Расширенные настройки** (нажмите «Show advanced settings»):

    | Настройка | По умолчанию | Описание |
    |-----------|-------------|----------|
    | **My Wave maximum tracks** | 150 | Сколько треков загружать для Моей волны. Меньше = быстрее загрузка. |
    | **Liked Tracks maximum tracks** | 500 | Сколько избранных треков показывать. Меньше = быстрее загрузка. |
    | **API Base URL** | `https://api.music.yandex.net` | Менять только если Яндекс изменит адрес API. |
    | **Locale override** | — | Переопределяет локаль для названий папок (напр. `ru_RU`). Оставьте пустым для использования локали Music Assistant. |

    ### Варианты качества

    | Значение | Название | Формат | Битрейт |
    |----------|----------|--------|---------|
    | `efficient` | Efficient | AAC | ~64 кбит/с |
    | `balanced` | Balanced | AAC | ~192 кбит/с |
    | `high` | High | MP3 | ~320 кбит/с |
    | `superb` | Superb | FLAC | Lossless |
