=== "English"

    # Browse Structure

    The provider maps the Yandex Music web interface into Music Assistant's Browse tree.
    Below is the full hierarchy with the equivalent URL on music.yandex.ru.

    ---

    ## Full tree

    ```
    Yandex Music
    ├── My Wave                          ← music.yandex.ru/radio/user/onyourwave
    │   ├── [tracks…]
    │   └── Load more
    │
    ├── For You                          ← music.yandex.ru (main page)
    │   ├── Picks                        ← music.yandex.ru/tag/<slug>
    │   │   ├── Mood                     (chill, sad, romantic, party, relax…)
    │   │   │   └── [tag → playlists]
    │   │   ├── Activity                 (workout, focus, morning, driving…)
    │   │   │   └── [tag → playlists]
    │   │   ├── Era                      (80s, 90s, 2000s, retro…)
    │   │   │   └── [tag → playlists]
    │   │   └── Genres                   (rock, jazz, classical, hip-hop…)
    │   │       └── [tag → playlists]
    │   └── Mixes                        ← music.yandex.ru/tag/<season>
    │       └── [seasonal tag → playlists]  (winter, summer, autumn…)
    │
    ├── Collection                       ← music.yandex.ru/users/<login>/
    │   ├── Tracks                       ← /likes/tracks
    │   ├── Artists                      ← /likes/artists
    │   ├── Albums                       ← /likes/albums
    │   └── Playlists                    ← /playlists
    │
    ├── Radio                            ← music.yandex.ru/radio
    │   ├── My Waves  [if available]     ← rotor/stations/dashboard (personalized)
    │   │   └── [station → tracks…]
    │   ├── genre                        ← music.yandex.ru/radio/genre/<tag>
    │   │   └── [station folders → tracks…]
    │   ├── mood                         ← music.yandex.ru/radio/mood/<tag>
    │   │   └── [station folders → tracks…]
    │   ├── activity                     ← music.yandex.ru/radio/activity/<tag>
    │   │   └── [station folders → tracks…]
    │   ├── epoch                        ← music.yandex.ru/radio/epoch/<tag>
    │   │   └── [station folders → tracks…]
    │   └── [other API-returned categories]
    │
    └── AI Wave Sets                     ← landing-blocks/mixes-waves
        └── [category]
            └── [wave station → tracks…]
    ```

    ---

    ## Section-by-section breakdown

    ### My Wave

    **Yandex equivalent:** "Моя волна" — the infinite personal radio on the Yandex Music home page and the Radio tab.

    - Tracks are fetched from Yandex Rotor API (`user:onyourwave` station).
    - A **Load more** button at the bottom fetches the next batch without reloading.
    - Rotor feedback (start / finish / skip) is sent automatically to improve future recommendations.
    - The folder name switches between "My Wave" and "Моя волна" based on the Music Assistant locale.

    See [My Wave](my-wave.md) for details.

    ---

    ### For You → Picks

    **Yandex equivalent:** Tag-based curated playlist collections — accessible at `music.yandex.ru/tag/<slug>` (e.g. `/tag/chill`, `/tag/rock`).

    - Tags are **discovered dynamically** from the Yandex Landing API; no hardcoded list is maintained.
    - Each tag is validated: only tags that actually return playlists are shown.
    - Tags are grouped into four categories using an internal mapping:

    | Category | Yandex web equivalent |
    |----------|-----------------------|
    | Mood | Thematic playlists (chill, party, sad…) |
    | Activity | Situational playlists (workout, focus, morning…) |
    | Era | Decade playlists (80s, 90s, 2000s…) |
    | Genres | Genre playlists (rock, jazz, electronic…) |

    - Category folders are hidden when no valid tags exist.
    - Discovery results are cached for **1 hour**; playlist contents for **10 minutes**.

    ---

    ### For You → Mixes

    **Yandex equivalent:** Seasonal editorial collections — `music.yandex.ru/tag/winter`, `/tag/summer`, etc.

    - Uses a fixed list of seasonal tags (`TAG_MIXES`), validated against the API.
    - Only seasons with active playlists are shown (e.g. "Winter" disappears in summer).

    ---

    ### Collection

    **Yandex equivalent:** User library — `music.yandex.ru/users/<login>/likes/tracks`, etc.

    Mirrors what is already synced into the Music Assistant library, giving a quick browse path to:

    | Folder | Library tab |
    |--------|-------------|
    | Tracks | Liked tracks |
    | Artists | Liked artists |
    | Albums | Liked albums |
    | Playlists | User playlists |

    Only folders for features enabled in the provider settings are shown.

    ---

    ### Radio

    **Yandex equivalent:** `music.yandex.ru/radio` — genre, mood, activity, and era radio stations.

    Stations are fetched from `rotor/stations/list` and grouped by their `category:tag` identifier.

    | Sub-folder | Examples |
    |------------|----------|
    | My Waves | Personalized station picks (from `rotor/stations/dashboard`) |
    | genre | rock, jazz, pop, electronic, classical… |
    | mood | energetic, calm, melancholic… |
    | activity | workout, study, party… |
    | epoch | 80s, 90s, 2000s… |

    - **My Waves** (personalized) appears only when the Yandex dashboard API returns stations.
    - Station folders have artwork from Yandex avatars and support playback directly.
    - Each station streams tracks via the Rotor API, infinite-radio style.

    ---

    ### AI Wave Sets

    **Yandex equivalent:** "AI Волны" / mixes-waves landing block — curated AI-generated wave sets grouped by theme.

    - Fetched from `landing-blocks/mixes-waves`.
    - Organized into category folders, each containing individual wave stations.
    - Each wave station plays like a radio (tracks stream from Rotor).

    ---

    ## Locale-aware naming

    All top-level folder names adapt to the Music Assistant language setting:

    | Locale | Language used |
    |--------|---------------|
    | `ru_*` | Russian (Моя волна, Для вас, Коллекция, Радио…) |
    | anything else | English (My Wave, For You, Collection, Radio…) |

    Folder names are resolved at runtime — no restart is needed after changing the MA locale.

    ---

    ## Caching summary

    | Data | Cache TTL |
    |------|-----------|
    | Tag discovery (picks) | 1 hour |
    | Tag playlist contents | 10 minutes |
    | Wave station list | 10 minutes |
    | Dashboard (My Waves) | 10 minutes |
    | AI Wave Sets | 10 minutes |
    | My Wave tracks batch | not cached (live) |

=== "Русский"

    # Структура Browse

    Провайдер отображает веб-интерфейс Яндекс Музыки в дерево Browse в Music Assistant.
    Ниже представлена полная иерархия с соответствующими URL на music.yandex.ru.

    ---

    ## Полное дерево

    ```
    Yandex Music
    ├── My Wave (Моя волна)              ← music.yandex.ru/radio/user/onyourwave
    │   ├── [треки…]
    │   └── Load more
    │
    ├── For You (Для вас)                ← music.yandex.ru (главная страница)
    │   ├── Picks (Подборки)             ← music.yandex.ru/tag/<slug>
    │   │   ├── Mood (Настроение)        (chill, sad, romantic, party, relax…)
    │   │   │   └── [тег → плейлисты]
    │   │   ├── Activity (Активность)    (workout, focus, morning, driving…)
    │   │   │   └── [тег → плейлисты]
    │   │   ├── Era (Эпоха)              (80s, 90s, 2000s, retro…)
    │   │   │   └── [тег → плейлисты]
    │   │   └── Genres (Жанры)           (rock, jazz, classical, hip-hop…)
    │   │       └── [тег → плейлисты]
    │   └── Mixes (Миксы)               ← music.yandex.ru/tag/<season>
    │       └── [сезонный тег → плейлисты]  (winter, summer, autumn…)
    │
    ├── Collection (Коллекция)           ← music.yandex.ru/users/<login>/
    │   ├── Tracks (Треки)               ← /likes/tracks
    │   ├── Artists (Исполнители)        ← /likes/artists
    │   ├── Albums (Альбомы)             ← /likes/albums
    │   └── Playlists (Плейлисты)        ← /playlists
    │
    ├── Radio (Радио)                    ← music.yandex.ru/radio
    │   ├── My Waves  [если доступно]    ← rotor/stations/dashboard (персональные)
    │   │   └── [станция → треки…]
    │   ├── genre (Жанры)               ← music.yandex.ru/radio/genre/<tag>
    │   │   └── [папки станций → треки…]
    │   ├── mood (Настроение)            ← music.yandex.ru/radio/mood/<tag>
    │   │   └── [папки станций → треки…]
    │   ├── activity (Активность)        ← music.yandex.ru/radio/activity/<tag>
    │   │   └── [папки станций → треки…]
    │   ├── epoch (Эпоха)               ← music.yandex.ru/radio/epoch/<tag>
    │   │   └── [папки станций → треки…]
    │   └── [другие категории API]
    │
    └── AI Wave Sets                     ← landing-blocks/mixes-waves
        └── [категория]
            └── [волна-станция → треки…]
    ```

    ---

    ## Описание разделов

    ### My Wave (Моя волна)

    **Аналог в Яндексе:** «Моя волна» — бесконечное персональное радио на главной странице и во вкладке «Радио».

    - Треки получаются через Rotor API Яндекса (станция `user:onyourwave`).
    - Кнопка **Load more** внизу загружает следующую пачку треков без перезагрузки.
    - Обратная связь о воспроизведении (старт / завершение / пропуск) отправляется автоматически.
    - Название папки переключается между «My Wave» и «Моя волна» в зависимости от локали Music Assistant.

    Подробнее — [My Wave](my-wave.md).

    ---

    ### For You → Picks (Для вас → Подборки)

    **Аналог в Яндексе:** Тематические подборки плейлистов — доступны по адресу `music.yandex.ru/tag/<slug>` (например, `/tag/chill`, `/tag/rock`).

    - Теги **обнаруживаются динамически** через Landing API Яндекса; фиксированный список не используется.
    - Каждый тег проверяется: отображаются только теги, для которых реально существуют плейлисты.
    - Теги распределяются по четырём категориям:

    | Категория | Аналог в Яндексе |
    |-----------|------------------|
    | Mood (Настроение) | Тематические плейлисты (chill, party, sad…) |
    | Activity (Активность) | Ситуативные плейлисты (workout, focus, morning…) |
    | Era (Эпоха) | Плейлисты по десятилетиям (80s, 90s, 2000s…) |
    | Genres (Жанры) | Жанровые плейлисты (rock, jazz, electronic…) |

    - Пустые категории скрываются.
    - Результаты обнаружения кэшируются на **1 час**; содержимое плейлистов — на **10 минут**.

    ---

    ### For You → Mixes (Для вас → Миксы)

    **Аналог в Яндексе:** Сезонные редакционные коллекции — `music.yandex.ru/tag/winter`, `/tag/summer` и т.д.

    - Используется фиксированный список сезонных тегов (`TAG_MIXES`), проверяемых через API.
    - Отображаются только сезоны с активными плейлистами (например, «Winter» исчезает летом).

    ---

    ### Collection (Коллекция)

    **Аналог в Яндексе:** Библиотека пользователя — `music.yandex.ru/users/<login>/likes/tracks` и т.д.

    Дублирует то, что уже синхронизировано в библиотеку Music Assistant, предоставляя быстрый путь для навигации:

    | Папка | Вкладка библиотеки |
    |-------|--------------------|
    | Tracks (Треки) | Понравившиеся треки |
    | Artists (Исполнители) | Понравившиеся исполнители |
    | Albums (Альбомы) | Понравившиеся альбомы |
    | Playlists (Плейлисты) | Плейлисты пользователя |

    Отображаются только папки для функций, включённых в настройках провайдера.

    ---

    ### Radio (Радио)

    **Аналог в Яндексе:** `music.yandex.ru/radio` — жанровые, настроенческие, активностные и эпохальные радиостанции.

    Станции получаются из `rotor/stations/list` и группируются по идентификатору `категория:тег`.

    | Подпапка | Примеры |
    |----------|---------|
    | My Waves | Персональные станции (из `rotor/stations/dashboard`) |
    | genre (Жанры) | rock, jazz, pop, electronic, classical… |
    | mood (Настроение) | energetic, calm, melancholic… |
    | activity (Активность) | workout, study, party… |
    | epoch (Эпоха) | 80s, 90s, 2000s… |

    - **My Waves** (персональные) отображается только если dashboard API возвращает станции.
    - Папки станций имеют обложки из аватаров Яндекса и поддерживают прямое воспроизведение.
    - Каждая станция стримит треки через Rotor API в режиме бесконечного радио.

    ---

    ### AI Wave Sets (AI Волны)

    **Аналог в Яндексе:** «AI Волны» / блок mixes-waves на лендинге — тематические AI-сгенерированные наборы волн.

    - Получаются из `landing-blocks/mixes-waves`.
    - Организованы в папки категорий, каждая из которых содержит отдельные волны-станции.
    - Каждая волна-станция воспроизводится как радио (треки стримятся через Rotor).

    ---

    ## Локализация названий

    Все названия папок верхнего уровня адаптируются к языку Music Assistant:

    | Локаль | Используемый язык |
    |--------|-------------------|
    | `ru_*` | Русский (Моя волна, Для вас, Коллекция, Радио…) |
    | любая другая | Английский (My Wave, For You, Collection, Radio…) |

    Названия разрешаются в runtime — перезапуск после смены локали MA не требуется.

    ---

    ## Сводная таблица кэширования

    | Данные | TTL кэша |
    |--------|----------|
    | Обнаружение тегов (подборки) | 1 час |
    | Содержимое плейлистов тегов | 10 минут |
    | Список радиостанций | 10 минут |
    | Dashboard (My Waves) | 10 минут |
    | AI Wave Sets | 10 минут |
    | Пачка треков Моей волны | не кэшируется (живой стрим) |
