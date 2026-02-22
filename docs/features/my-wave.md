# My Wave

=== "English"

    My Wave is Yandex Music's personalized infinite radio. It uses Yandex's Rotor recommendation engine to generate a continuous stream of tracks tailored to your listening habits.

    ### How it works

    1. When you open My Wave, the provider requests several batches of tracks from Yandex's Rotor API (the same engine behind "My Wave" in the official Yandex Music app).
    2. Each batch contains a few tracks. The provider fetches multiple batches at once to give you a longer playlist to start with.
    3. Duplicate tracks are automatically filtered out — if a track appeared in a previous batch, it won't show up again.
    4. In Browse, a **"Load more"** button appears at the bottom. Tapping it fetches the next batch and adds more tracks.
    5. The maximum number of tracks is configurable (default: 150). Once the limit is reached, no more tracks are loaded.

    ### Improving your recommendations

    The provider sends playback feedback to Yandex, similar to what the official app does:

    - When you **start playing** a track, Yandex is notified.
    - When you **finish** a track (listen to nearly the end), Yandex counts it as "liked."
    - When you **skip** a track (stop before the end), Yandex adjusts future recommendations accordingly.

    This feedback happens automatically — you don't need to do anything. Over time, Yandex learns your preferences and My Wave becomes more personalized.

    ### Where My Wave appears

    - **Browse** — A "My Wave" folder at the root of Yandex Music. You can play it directly or browse individual tracks.
    - **Home page (Discover)** — A "My Wave" recommendation section with a selection of personalized tracks.
    - **Library playlists** — A virtual "My Wave" playlist always appears in your playlist list for quick access.

    ### Locale-based folder name

    The folder name adapts automatically to your Music Assistant language:

    - **Russian** (`ru_*` locales): "Моя волна"
    - **Other locales**: "My Wave"

    ### Similar tracks (Radio mode)

    When you start radio mode from any Yandex Music track, the provider uses Yandex's Rotor engine to find similar tracks. This works for any track, not just My Wave — it creates a station based on that specific track's style and genre.

=== "Русский"

    Моя волна — персонализированное бесконечное радио Yandex Music. Оно использует рекомендательный движок Rotor от Яндекса для генерации непрерывного потока треков, подобранных под ваши музыкальные предпочтения.

    ### Как это работает

    1. При открытии Моей волны провайдер запрашивает несколько пачек треков через Rotor API Яндекса (тот же движок, что стоит за «Моей волной» в официальном приложении Yandex Music).
    2. Каждая пачка содержит несколько треков. Провайдер загружает несколько пачек сразу, чтобы сформировать более длинный плейлист.
    3. Дубликаты автоматически отфильтровываются — если трек уже был в предыдущей пачке, он не появится снова.
    4. В Browse внизу отображается кнопка **«Load more»**. Нажатие загружает следующую пачку и добавляет новые треки.
    5. Максимальное количество треков настраивается (по умолчанию: 150). При достижении лимита загрузка прекращается.

    ### Улучшение рекомендаций

    Провайдер отправляет обратную связь о воспроизведении в Яндекс, аналогично официальному приложению:

    - При **начале воспроизведения** трека Яндекс получает уведомление.
    - При **завершении** трека (прослушивании до конца) Яндекс засчитывает его как «понравившийся».
    - При **пропуске** трека (остановка до окончания) Яндекс корректирует будущие рекомендации.

    Обратная связь отправляется автоматически — никаких действий не требуется. Со временем Яндекс изучает ваши предпочтения, и Моя волна становится более персонализированной.

    ### Где отображается Моя волна

    - **Browse** — папка «Моя волна» в корне Yandex Music. Можно запустить воспроизведение напрямую или просматривать отдельные треки.
    - **Главная страница (Discover)** — секция рекомендаций «My Wave» с подборкой персонализированных треков.
    - **Плейлисты библиотеки** — виртуальный плейлист «Моя волна» всегда отображается в списке плейлистов для быстрого доступа.

    ### Локализованное название папки

    Название папки автоматически адаптируется к языку Music Assistant:

    - **Русский** (локали `ru_*`): «Моя волна»
    - **Другие локали**: «My Wave»

    ### Похожие треки (режим радио)

    При запуске режима радио с любого трека Yandex Music провайдер использует движок Rotor для поиска похожих треков. Это работает для любого трека, не только для Моей волны — создаётся станция на основе стиля и жанра конкретного трека.
