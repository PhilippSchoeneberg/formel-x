# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

**FormelX** is a mobile chemistry learning app (Android, published as an `.aab` via Buildozer) written in Python with **Kivy + KivyMD 2.x** (Material 3). Users learn in three modes:

- **Elements** – tap the right element on a periodic table (learning mode) or browse/select which elements belong to a group (remembering mode).
- **Compounds** – multiple choice: formula → name or name → formula.
- **Questions** – free-form multiple-choice questions.

Content is organised into **groups** (like courses). A logged-in account *owns* groups and can create/edit/delete their content. Anonymous users can *add* existing groups by name and only learn.

The backend is **Supabase** (PostgREST), accessed directly over HTTP with `httpx`.

## Running

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # once
.venv/bin/python main.py
```

Run from the repo root — all file paths (`assets/`, `src/kivy/*.kv`, `src/utils/state.json`) are relative to the CWD. The app needs network access to Supabase at startup.

- Python ≥ 3.11 (3.13 works). `requirements.txt` holds the desktop deps; Android deps are in `buildozer.spec` `requirements`.
- `bcrypt` must stay pinned to `4.0.1`: `passlib` 1.7.4 crashes on hashing with bcrypt ≥ 4.1, which breaks login/registration.
- **KivyMD is pinned to upstream commit `d2f7740`** (reports as `2.0.1.dev0`) via a GitHub archive URL in both `requirements.txt` and `buildozer.spec`. Don't swap it for PyPI `kivymd` 2.0.0: that release branched off separately from this commit and hasn't been tested with the app. This commit requires `asynckivy>=0.6,<0.7`, so `asynckivy==0.6.4` / `asyncgui==0.6.3` are pinned too. When changing the KivyMD pin, update both files together.
- There are no tests.

## Building / releasing (Android)

`make build-android` runs: `buildozer android release` → rename to `bin/formelx-release.aab` → `jarsigner` with `my-release-key.keystore` (alias `my-key-alias`) → `zipalign` to `bin/formelx-release-aligned.aab`. Before each release, bump `android.numeric_version` in `buildozer.spec` (currently `4`). `make clean` deletes `bin/`.

When adding new file types that must ship in the APK, add the extension to `source.include_exts` in `buildozer.spec`. New pip deps must be added to `requirements` there too.

## Architecture

```
main.py                   MainApp(MDApp): state, theme, language, login/logout, global menu, screen wiring
src/screens/              One SafeScreen subclass per screen (logic)
src/kivy/                 Matching .kv layout per screen (loaded explicitly in MainApp.build)
src/popups/               MDDialog subclasses for create/edit/delete/login flows
src/database/database.py  Database class: thin PostgREST wrapper (one method per CRUD op)
src/database/*.sql        Supabase schema (setup.sql) + element seed data (insert_elements.sql)
src/utils/                enums, i18n LanguageManager, JSON state persistence, formula → unicode, .po compiler
assets/<lang>/LC_MESSAGES/texts.po|.mo   Translations (de, en, es, fr, nl)
```

### Key conventions

- **Global app object**: everything goes through `App.get_running_app()` (stored as `self.app`). It holds `db`, `language_manager`, `state`, `logged_in_user_id`, `logged_in_group`, `groups`, `learning_mode`, `formula_to_name_query_mode`, and direct references to every screen (`app.modes_menu_screen`, `app.compound_menu_screen`, …).
- **Screen names** (used with `app.change_screen(name)` / `root.get_screen(name)`): `modesMenu`, `elementMenu`, `compoundMenu`, `compoundLearning`, `questionMenu`, `questionLearning`. The `ScreenManager` is built in Python in `MainApp.build()`, not from `main.kv`.
- **Screens** subclass `SafeScreen` (`src/screens/safe_screen.py`), which pads `ids.main_box` for Android status/nav bars and iOS notches. Every `.kv` screen layout must have a root `BoxLayout` with `id: main_box`, and a `general_menu_button` id if the global menu is used.
- Each screen implements `refresh()` (called on language change / group change via `app.screens`). Menu screens with editable content implement `create(caller)`, `edit()`, `delete()` — the global hamburger menu (`MainApp.general_menu_open`) calls these on the *current* screen when a user is logged in.
- **Adding a screen**: create `src/screens/x.py` + `src/kivy/x.kv`, add the kv path to `kv_files` in `MainApp.build()`, instantiate it, add it to the `ScreenManager` and (if it needs refresh/theme) to `self.screens`.
- **Popups** are `MDDialog` subclasses built in `__init__`; they are instantiated fresh per use (`SomePopupMenu().open(...)`), override `open(...)` to receive context and `dismiss()` to reset fields. Validation errors use the pattern `field.error = False; field.error = True` to re-trigger the error state.
- **Data shapes**: DB rows are passed around as plain dicts (`group`, `category`, `compound`, `question`, `element`). `Database` methods take the dicts (e.g. `group["id"]`) rather than ids in most places.
- **Enums** (`src/utils/enums.py`): `CategoryTypes` (compound=0, question=1) stored as int; `DifficultyTypes` values `"easy"|"medium"|"hard"` stored as text and also used as translation keys.
- **Formulas** are entered in a LaTeX-like notation and rendered with `transform_to_unicode`: `H_2O`, `SO_4^{2-}` → `H₂O`, `SO₄²⁻`.
- **UI colours for answers**: correct = `[0, 1, 0, 0.3]`, wrong = `[1, 0, 0, 0.3]` with `theme_bg_color = "Custom"`. Theme palettes: `"Darkblue"` / `"Lightblue"`; all fonts are overridden to the bundled Roboto variable font.

### Internationalisation

- All user-visible strings go through `app.language_manager.translate("key")` — keys are snake_case msgids, not English text. Strings are often built by concatenation (`translate("select") + translate("category")`), so many translations carry intentional trailing/leading spaces (e.g. `"Wähle "`, `" darf nicht leer sein."`). Preserve them.
- When adding a key, add it to **all five** `assets/*/LC_MESSAGES/texts.po` files, then recompile the `.mo` files (both are committed):
  ```bash
  python src/utils/compile_po_files.py
  ```
- Available languages are discovered from the subdirectories of `assets/`. Element names from the DB (`hydrogen`, …) are also translated as keys.

### Persistence

- **Local state**: `src/utils/state.json` (`dark_mode`, `language`, `logged_in_user_id`, `logged_in_group`, `groups`) via `load_state`/`save_state`. It is tracked in git and rewritten at runtime, so it often shows up in diffs — avoid committing personal state changes. `MainApp.__init__` expects the `language` and `dark_mode` keys to exist.
- **Remote DB**: Supabase tables `accounts`, `groups`, `elements`, `elements_to_groups`, `categories`, `compounds`, `questions` (see `setup.sql`). Authentication is custom: passwords are bcrypt-hashed client-side (`passlib`) and stored in `accounts`; Supabase Auth is not used. Content tables are scoped by `group_id`; compounds/questions also reference `category_id`. Compounds/questions have one correct + 2 required + 2 optional wrong options.
- Database calls are **synchronous** on the UI thread. Network failures (offline, DNS, timeout) raise `DatabaseConnectionError` (from a custom httpx transport in `database.py`). A Kivy `ExceptionManager` handler in `main.py` catches it anywhere in the main loop and calls `app.show_connection_error()`. `on_start` runs before the main loop, so `load_initial_data()` catches it itself and retries when the user taps "Okay". Don't catch `DatabaseConnectionError` locally and return empty data instead: anonymous users' saved groups are removed when `group_exists_by_id` returns False.
- HTTP error responses (4xx/5xx) are **not** handled: their JSON body is a dict, not a list, so callers fail with `TypeError`/`KeyError`.

## Known issues / gotchas (verify before relying on them)

- `src/kivy/main.kv` is loaded but its root `ScreenManager` is unused, and it declares `CompoundLearningScreen` for `questionLearning`.
- `DifficultyTypes` members are named `difficulty0`, `difficulty1`, `difficulty3` (no `difficulty2`).
- The Supabase URL + anon key are hard-coded in `main.py`, and the release keystore is committed. Don't add further secrets to the repo, and don't print/echo them.
- `.idea/` is partly tracked (IDE config); avoid committing unrelated changes there.

## Git

- Default branch: `main`. Commit messages are short imperative English sentences (e.g. "Fix the refreshing of categories after creation.").
