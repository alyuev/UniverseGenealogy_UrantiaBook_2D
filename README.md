# Космология Книги Урантии

**Открыть схему:** https://alyuev.github.io/UniverseGenealogy_UrantiaBook_2D/

Скачать один файл: раздел [Releases](https://github.com/alyuev/UniverseGenealogy_UrantiaBook_2D/releases) → `cosmology.html`.

Встроить на сайт:

    <iframe src="https://alyuev.github.io/UniverseGenealogy_UrantiaBook_2D/dist/cosmology.html" style="width:100%;height:85vh;border:0"></iframe>

Интерактивная схема: административные единицы от Рая до Урантии, личности от Божеств до человека,
связи происхождения, служения и восхождения. Языки: русский (перевод Фонда Урантии) и английский; светлая и тёмная темы.

- `dist/cosmology.html` — готовая схема, один файл: открывается без сервера, можно скачать или встроить на сайт.
- `data/cosmology.yaml` — структура; `data/lang/<язык>.yaml` — тексты.
- `src/engine.html` — движок отображения.

Сборка после правки данных:

    python tools/validate.py   # проверка структуры и терминов по book.db
    python tools/build.py      # собирает dist/cosmology.html
