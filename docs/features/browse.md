=== "English"

    # Browse Structure

    The provider maps the Yandex Music API into Music Assistant's Browse tree.
    Below is the full hierarchy with the actual API endpoint each section is backed by.

    ---

    ## Full tree

    ```
    Yandex Music
    ├── My Wave                          ← rotor/station/user:onyourwave/tracks
    │   ├── [tracks…]
    │   └── Load more
    │
    ├── For You                          ← (container folder)
    │   ├── Picks                        ← landing("mixes") + tags(<slug>)
    │   │   ├── Mood                     (chill, sad, romantic, party, relax…)
    │   │   │   └── [tag → tags(<slug>).playlists]
    │   │   ├── Activity                 (workout, focus, morning, driving…)
    │   │   │   └── [tag → tags(<slug>).playlists]
    │   │   ├── Era                      (80s, 90s, 2000s, retro…)
    │   │   │   └── [tag → tags(<slug>).playlists]
    │   │   └── Genres                   (rock, jazz, classical, hip-hop…)
    │   │       └── [tag → tags(<slug>).playlists]
    │   └── Mixes                        ← tags(<season>).playlists
    │       └── [seasonal tag → playlists]  (winter, summer, autumn…)
    │
    ├── Collection                       ← (container folder)
    │   ├── Tracks                       ← users/[uid]/likes/tracks
    │   ├── Artists                      ← users/[uid]/likes/artists
    │   ├── Albums                       ← users/[uid]/likes/albums
    │   └── Playlists                    ← users/[uid]/playlists
    │
    ├── Radio                            ← rotor/stations/list
    │   ├── My Waves  [if available]     ← rotor/stations/dashboard
    │   │   └── [station → rotor/station/<id>/tracks]
    │   ├── genre                        ← rotor/stations/list (category=genre)
    │   │   └── [station → rotor/station/genre:<tag>/tracks]
    │   ├── mood                         ← rotor/stations/list (category=mood)
    │   │   └── [station → rotor/station/mood:<tag>/tracks]
    │   ├── activity                     ← rotor/stations/list (category=activity)
    │   │   └── [station → rotor/station/activity:<tag>/tracks]
    │   ├── epoch                        ← rotor/stations/list (category=epoch)
    │   │   └── [station → rotor/station/epoch:<tag>/tracks]
    │   └── [other API-returned categories]
    │
    └── AI Wave Sets                     ← landing-blocks/mixes-waves
        └── [category]
            └── [wave station → rotor/station/<id>/tracks]
    ```

    ---

    ## Section-by-section breakdown

    ### My Wave

    **API:** `rotor/station/user:onyourwave/tracks`

    - Tracks are fetched from Yandex Rotor API (`user:onyourwave` station).
    - A **Load more** button at the bottom fetches the next batch without reloading.
    - Rotor feedback (start / finish / skip) is sent automatically to improve future recommendations.
    - The folder name switches between "My Wave" and "Моя волна" based on the Music Assistant locale.

    See [My Wave](my-wave.md) for details.

    ---

    ### For You → Picks

    **API:** Tag discovery — `landing("mixes")`; tag validation and playlists — `tags(<slug>)`

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

    **API:** `tags(<season>)` — playlists for each seasonal tag (`winter`, `summer`, `autumn`…)

    - Uses a fixed list of seasonal tags (`TAG_MIXES`), validated against the API.
    - Only seasons with active playlists are shown (e.g. "Winter" disappears in summer).

    ---

    ### Collection

    **API:** `users/[uid]/likes/tracks`, `users/[uid]/likes/artists`, `users/[uid]/likes/albums`, `users/[uid]/playlists`

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

    **API:** Station list — `rotor/stations/list`; tracks — `rotor/station/<category>:<tag>/tracks`

    Stations are fetched from `rotor/stations/list` and grouped by their `category:tag` identifier.

    | Sub-folder | API | Examples |
    |------------|-----|----------|
    | My Waves | `rotor/stations/dashboard` | Personalized station picks |
    | genre | `rotor/stations/list` (category=genre) | rock, jazz, pop… |
    | mood | `rotor/stations/list` (category=mood) | energetic, calm… |
    | activity | `rotor/stations/list` (category=activity) | workout, study… |
    | epoch | `rotor/stations/list` (category=epoch) | 80s, 90s… |

    - **My Waves** (personalized) appears only when the Yandex dashboard API returns stations.
    - Station folders have artwork from Yandex avatars and support playback directly.
    - Each station streams tracks via the Rotor API, infinite-radio style.

    ---

    ### AI Wave Sets

    **API:** `landing-blocks/mixes-waves`

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

    Провайдер отображает данные Yandex Music API в дерево Browse в Music Assistant.
    Ниже представлена полная иерархия с реальным API-эндпоинтом каждого раздела.

    ---

    ## Полное дерево

    ```
    Yandex Music
    ├── My Wave (Моя волна)              ← rotor/station/user:onyourwave/tracks
    │   ├── [треки…]
    │   └── Load more
    │
    ├── For You (Для вас)                ← (папка-контейнер)
    │   ├── Picks (Подборки)             ← landing("mixes") + tags(<slug>)
    │   │   ├── Mood (Настроение)        (chill, sad, romantic, party, relax…)
    │   │   │   └── [тег → tags(<slug>).playlists]
    │   │   ├── Activity (Активность)    (workout, focus, morning, driving…)
    │   │   │   └── [тег → tags(<slug>).playlists]
    │   │   ├── Era (Эпоха)              (80s, 90s, 2000s, retro…)
    │   │   │   └── [тег → tags(<slug>).playlists]
    │   │   └── Genres (Жанры)           (rock, jazz, classical, hip-hop…)
    │   │       └── [тег → tags(<slug>).playlists]
    │   └── Mixes (Миксы)               ← tags(<season>).playlists
    │       └── [сезонный тег → плейлисты]  (winter, summer, autumn…)
    │
    ├── Collection (Коллекция)           ← (папка-контейнер)
    │   ├── Tracks (Треки)               ← users/[uid]/likes/tracks
    │   ├── Artists (Исполнители)        ← users/[uid]/likes/artists
    │   ├── Albums (Альбомы)             ← users/[uid]/likes/albums
    │   └── Playlists (Плейлисты)        ← users/[uid]/playlists
    │
    ├── Radio (Радио)                    ← rotor/stations/list
    │   ├── My Waves  [если доступно]    ← rotor/stations/dashboard
    │   │   └── [станция → rotor/station/<id>/tracks]
    │   ├── genre (Жанры)               ← rotor/stations/list (category=genre)
    │   │   └── [станция → rotor/station/genre:<tag>/tracks]
    │   ├── mood (Настроение)            ← rotor/stations/list (category=mood)
    │   │   └── [станция → rotor/station/mood:<tag>/tracks]
    │   ├── activity (Активность)        ← rotor/stations/list (category=activity)
    │   │   └── [станция → rotor/station/activity:<tag>/tracks]
    │   ├── epoch (Эпоха)               ← rotor/stations/list (category=epoch)
    │   │   └── [станция → rotor/station/epoch:<tag>/tracks]
    │   └── [другие категории API]
    │
    └── AI Wave Sets                     ← landing-blocks/mixes-waves
        └── [категория]
            └── [волна-станция → rotor/station/<id>/tracks]
    ```

    ---

    ## Описание разделов

    ### My Wave (Моя волна)

    **API:** `rotor/station/user:onyourwave/tracks`

    - Треки получаются через Rotor API Яндекса (станция `user:onyourwave`).
    - Кнопка **Load more** внизу загружает следующую пачку треков без перезагрузки.
    - Обратная связь о воспроизведении (старт / завершение / пропуск) отправляется автоматически.
    - Название папки переключается между «My Wave» и «Моя волна» в зависимости от локали Music Assistant.

    Подробнее — [My Wave](my-wave.md).

    ---

    ### For You → Picks (Для вас → Подборки)

    **API:** Обнаружение тегов — `landing("mixes")`; валидация и плейлисты — `tags(<slug>)`

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

    **API:** `tags(<season>)` — плейлисты для каждого сезонного тега (`winter`, `summer`, `autumn`…)

    - Используется фиксированный список сезонных тегов (`TAG_MIXES`), проверяемых через API.
    - Отображаются только сезоны с активными плейлистами (например, «Winter» исчезает летом).

    ---

    ### Collection (Коллекция)

    **API:** `users/[uid]/likes/tracks`, `users/[uid]/likes/artists`, `users/[uid]/likes/albums`, `users/[uid]/playlists`

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

    **API:** Список станций — `rotor/stations/list`; треки — `rotor/station/<category>:<tag>/tracks`

    Станции получаются из `rotor/stations/list` и группируются по идентификатору `категория:тег`.

    | Подпапка | API | Примеры |
    |----------|-----|---------|
    | My Waves | `rotor/stations/dashboard` | Персональные станции |
    | genre (Жанры) | `rotor/stations/list` (category=genre) | rock, jazz, pop… |
    | mood (Настроение) | `rotor/stations/list` (category=mood) | energetic, calm… |
    | activity (Активность) | `rotor/stations/list` (category=activity) | workout, study… |
    | epoch (Эпоха) | `rotor/stations/list` (category=epoch) | 80s, 90s… |

    - **My Waves** (персональные) отображается только если dashboard API возвращает станции.
    - Папки станций имеют обложки из аватаров Яндекса и поддерживают прямое воспроизведение.
    - Каждая станция стримит треки через Rotor API в режиме бесконечного радио.

    ---

    ### AI Wave Sets (AI Волны)

    **API:** `landing-blocks/mixes-waves`

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
