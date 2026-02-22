=== "English"

    # Picks & Mixes

    Picks and Mixes let you browse curated playlists organized by theme, available in the Browse section.

    ### Browse structure

    ```
    Yandex Music
    ├── Picks
    │   ├── Mood      (e.g. Chill, Sad, Romantic, Party, Relax, ...)
    │   ├── Activity  (e.g. Workout, Focus, Morning, Evening, Driving, ...)
    │   ├── Era       (e.g. 80s, 90s, 2000s, Retro, ...)
    │   └── Genres    (e.g. Rock, Jazz, Classical, Electronic, R&B, Hip-Hop, ...)
    └── Mixes
        └── Seasonal  (e.g. Winter, Summer, Autumn, New Year, ...)
    ```

    ### Dynamic tag discovery

    All tags are **discovered dynamically** from the Yandex Music Landing API — the provider does not rely on a hardcoded list. Only tags that Yandex actually returns are shown, which means:

    - **No empty folders** — if a tag doesn't exist in the current API response, it simply won't appear
    - **New tags appear automatically** — when Yandex adds new curated collections, they show up without a provider update
    - **Categories are hidden when empty** — if no tags were discovered for a category (e.g. Era), the folder is not shown

    Discovered tags are categorized into Mood, Activity, Era, or Genres using an internal mapping. Tags not in the mapping default to the Mood category. Useless tags (like "Albums with video shots") are blacklisted and filtered out.

    Tag discovery results are cached for 1 hour. Tag playlist contents are cached for 10 minutes.

    ### Playback behavior

    Category and tag folders have **Play disabled** (`is_playable=False`). This prevents accidentally queuing thousands of tracks when pressing Play on a folder that contains playlists. To play music, navigate into a specific tag and choose a playlist.

=== "Русский"

    # Подборки и Миксы

    Подборки и Миксы позволяют просматривать тематические плейлисты в разделе Browse.

    ### Структура Browse

    ```
    Yandex Music
    ├── Подборки (Picks)
    │   ├── Настроение  (напр. Chill, Sad, Romantic, Party, Relax, ...)
    │   ├── Активность   (напр. Workout, Focus, Morning, Evening, Driving, ...)
    │   ├── Эпоха        (напр. 80s, 90s, 2000s, Retro, ...)
    │   └── Жанры        (напр. Rock, Jazz, Classical, Electronic, R&B, Hip-Hop, ...)
    └── Миксы (Mixes)
        └── Сезонные     (напр. Winter, Summer, Autumn, New Year, ...)
    ```

    ### Динамическое обнаружение тегов

    Все теги **обнаруживаются динамически** через Landing API Yandex Music — провайдер не использует фиксированный список. Показываются только теги, которые Яндекс реально вернул, что означает:

    - **Нет пустых папок** — если тег не существует в текущем ответе API, он просто не отображается
    - **Новые теги появляются автоматически** — когда Яндекс добавляет новые подборки, они показываются без обновления провайдера
    - **Пустые категории скрываются** — если для категории (например, Эпоха) не нашлось ни одного тега, папка не отображается

    Обнаруженные теги распределяются по категориям Настроение, Активность, Эпоха, Жанры через внутренний маппинг. Теги вне маппинга попадают в категорию Настроение. Бесполезные теги (например, «Альбомы с видеошотами») добавлены в чёрный список и отфильтровываются.

    Результаты обнаружения тегов кэшируются на 1 час. Содержимое плейлистов тегов кэшируется на 10 минут.

    ### Поведение воспроизведения

    У папок категорий и тегов **отключена кнопка Play** (`is_playable=False`). Это предотвращает случайную загрузку тысяч треков при нажатии Play на папке, содержащей плейлисты. Для воспроизведения музыки нужно зайти в конкретный тег и выбрать плейлист.
