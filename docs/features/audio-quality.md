=== "English"

    # Audio Quality

    Four quality tiers are available:

    | Quality | Format | Bitrate | Requirements |
    |---------|--------|---------|--------------|
    | Efficient | AAC | ~64 kbps | Free account |
    | Balanced (default) | AAC | ~192 kbps | Free account |
    | High | MP3 | ~320 kbps | Free account |
    | Superb | FLAC | Lossless | Plus subscription |

    You can change the quality at any time in the provider settings. The actual codec and bitrate are selected automatically when playback starts, based on what Yandex Music offers for each track.

    Encrypted FLAC tracks are decrypted on-the-fly as data arrives. Seeking is handled by Music Assistant core via ffmpeg.

    ### FLAC Streaming Modes

    | Mode | Description |
    |------|-------------|
    | **Direct** | Data is streamed directly from Yandex without buffering. Lowest memory usage. |
    | **Buffered** | Data is read into a memory buffer before being passed to Music Assistant. Reduces stalls on slow connections. |
    | **Preload** | The entire track is downloaded before playback begins. Most reliable but uses more memory and increases start-up time. |

    ### Stream buffer size (MB)

    When using **Buffered** mode, the **Stream buffer size (MB)** setting controls how much data is held in memory at once. The default is 8 MB, which provides approximately 45 seconds of FLAC audio. Increase this value if you experience playback stalls on slow connections.

=== "Русский"

    # Качество аудио

    Доступны четыре уровня качества:

    | Качество | Формат | Битрейт | Требования |
    |----------|--------|---------|------------|
    | Efficient | AAC | ~64 кбит/с | Бесплатный аккаунт |
    | Balanced (по умолчанию) | AAC | ~192 кбит/с | Бесплатный аккаунт |
    | High | MP3 | ~320 кбит/с | Бесплатный аккаунт |
    | Superb | FLAC | Lossless | Подписка Plus |

    Качество можно изменить в любое время в настройках провайдера. Кодек и битрейт выбираются автоматически при начале воспроизведения в зависимости от того, что Yandex Music предлагает для каждого трека.

    Зашифрованные FLAC-треки дешифруются на лету по мере поступления данных. Перемотка обрабатывается ядром Music Assistant через ffmpeg.

    ### Режимы FLAC-стриминга

    | Режим | Описание |
    |-------|----------|
    | **Direct** | Данные передаются напрямую из Яндекса без буферизации. Минимальное использование памяти. |
    | **Buffered** | Данные считываются в буфер памяти перед передачей в Music Assistant. Снижает зависания при медленном соединении. |
    | **Preload** | Весь трек загружается перед началом воспроизведения. Наиболее надёжный режим, но использует больше памяти и увеличивает время начала воспроизведения. |

    ### Размер буфера потока (МБ)

    При использовании режима **Buffered** параметр **Stream buffer size (MB)** определяет объём данных, удерживаемых в памяти одновременно. По умолчанию — 8 МБ, что соответствует примерно 45 секундам FLAC-аудио. Увеличьте это значение при зависаниях воспроизведения на медленном соединении.
