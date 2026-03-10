# Frontend Pages Documentation

## 1. Scope and Goal

Документ описывает все страницы frontend, которые уже реализованы в проекте:

- какие страницы есть;
- по каким URL они доступны;
- откуда берутся (native React или Stitch export);
- где лежат исходные и сгенерированные файлы;
- как обновлять/добавлять новые страницы безопасно.

---

## 2. Current Runtime Routing

Маршрутизация сделана вручную в `src/main.jsx` через `window.location.pathname`.

### Route map

| URL path | Page type | Source |
|---|---|---|
| `/` | Native React page | `src/App.jsx` |
| `/doctor-directory-with-filters-ru` | Independent Stitch page | `public/stitch/doctor-directory-with-filters-ru.html` |
| `/doctor-public-profile-ru` | Independent Stitch page | `public/stitch/doctor-public-profile-ru.html` |
| `/public-questions-feed-ru` | Independent Stitch page | `public/stitch/public-questions-feed-ru.html` |
| `/login-desktop-ru` | Independent Stitch page | `public/stitch/login-desktop-ru.html` |
| `/registration-desktop-ru` | Independent Stitch page | `public/stitch/registration-desktop-ru.html` |

---

## 3. Page Inventory

## 3.1 Main Landing (native)

- **Route:** `/`
- **Implementation:** full native React/JSX (no iframe)
- **Files:**
  - `src/App.jsx`
  - `src/App.css`

---

## 3.2 Doctor Directory with Filters (RU)

- **Stitch screen ID:** `9871202d4c1b4b46a0fb6bb7af520bdf`
- **Route:** `/doctor-directory-with-filters-ru`
- **Wrapper component:** `src/DoctorDirectoryWithFiltersPage.jsx`
- **Served HTML:** `public/stitch/doctor-directory-with-filters-ru.html`
- **Preview image:** `public/stitch/doctor-directory-with-filters-ru.png`
- **Raw artifacts:**
  - `stitch/raw/doctor-directory-with-filters-ru-screen-code-response.json`
  - `stitch/raw/doctor-directory-with-filters-ru-screen-image-response.json`
  - `stitch/raw/doctor-directory-with-filters-ru.html`
  - `stitch/raw/doctor-directory-with-filters-ru-hosted-urls.txt`

---

## 3.3 Doctor Public Profile (RU)

- **Stitch screen ID:** `d4ff542a39c448f9803dd23cc14d2a32`
- **Route:** `/doctor-public-profile-ru`
- **Wrapper component:** `src/DoctorPublicProfilePage.jsx`
- **Served HTML:** `public/stitch/doctor-public-profile-ru.html`
- **Preview image:** `public/stitch/doctor-public-profile-ru.png`
- **Raw artifacts:**
  - `stitch/raw/doctor-public-profile-ru-screen-code-response.json`
  - `stitch/raw/doctor-public-profile-ru-screen-image-response.json`
  - `stitch/raw/doctor-public-profile-ru.html`
  - `stitch/raw/doctor-public-profile-ru-hosted-urls.txt`

---

## 3.4 Public Questions Feed (RU)

- **Stitch screen ID:** `a179243b938345b2a10fb4d7608e0a5e`
- **Route:** `/public-questions-feed-ru`
- **Wrapper component:** `src/PublicQuestionsFeedPage.jsx`
- **Served HTML:** `public/stitch/public-questions-feed-ru.html`
- **Preview image:** `public/stitch/public-questions-feed-ru.png`
- **Raw artifacts:**
  - `stitch/raw/public-questions-feed-ru-screen-code-response.json`
  - `stitch/raw/public-questions-feed-ru-screen-image-response.json`
  - `stitch/raw/public-questions-feed-ru.html`
  - `stitch/raw/public-questions-feed-ru-hosted-urls.txt`

---

## 3.5 Login (Desktop)

- **Stitch screen ID:** `14fe5d2debf248baabc172593526281e`
- **Route:** `/login-desktop-ru`
- **Wrapper component:** `src/LoginDesktopPage.jsx`
- **Served HTML:** `public/stitch/login-desktop-ru.html`
- **Preview image:** `public/stitch/login-desktop-ru.png`
- **Raw artifacts:**
  - `stitch/raw/login-desktop-ru-screen-code-response.json`
  - `stitch/raw/login-desktop-ru-screen-image-response.json`
  - `stitch/raw/login-desktop-ru.html`
  - `stitch/raw/login-desktop-ru-hosted-urls.txt`
- **Manual adjustment (important):**
  - удалён блок social login (`Или продолжить с`, `Google`, `ВКонтакте`) по требованию.

---

## 3.6 Registration (Desktop)

- **Stitch screen ID:** `5f926a656fa04515b7c0a195cbca6953`
- **Route:** `/registration-desktop-ru`
- **Wrapper component:** `src/RegistrationDesktopPage.jsx`
- **Served HTML:** `public/stitch/registration-desktop-ru.html`
- **Preview image:** `public/stitch/registration-desktop-ru.png`
- **Raw artifacts:**
  - `stitch/raw/registration-desktop-ru-screen-code-response.json`
  - `stitch/raw/registration-desktop-ru-screen-image-response.json`
  - `stitch/raw/registration-desktop-ru.html`
  - `stitch/raw/registration-desktop-ru-hosted-urls.txt`

---

## 4. Technical Pattern Used for Stitch Pages

Каждая Stitch-страница реализована одинаково:

1. React wrapper-компонент с полноэкранным `iframe`.
2. `iframe` указывает на `public/stitch/<slug>.html`.
3. Route добавляется в `pageByPath` внутри `src/main.jsx`.
4. PNG хранится рядом в `public/stitch/<slug>.png` для reference.

Плюсы текущего подхода:

- быстрое подключение новых экранов;
- минимум риска сломать текущий native layout;
- 1:1 визуал относительно Stitch export.

Ограничения:

- экран внутри `iframe` сложнее интегрировать с общими React state/router;
- поведение ограничено самим Stitch HTML;
- для тесной интеграции нужно переводить страницу в native JSX.

---

## 5. Folder Conventions

### `public/stitch/`

Хранит runtime-ассеты, которые реально отдаются браузеру:

- `*.html` — stitched страницы;
- `*.png` — скриншоты для reference.

### `stitch/raw/`

Хранит артефакты импорта из Stitch:

- `*-screen-code-response.json`
- `*-screen-image-response.json`
- `*.html` (сырой скачанный HTML)
- `*-hosted-urls.txt` (источник URL).

---

## 6. How to Add a New Stitch Page

1. Получить code/image payload через Stitch MCP (`get_screen_code`, `get_screen_image`).
2. Извлечь `htmlCode.downloadUrl` и `screenshot.downloadUrl`.
3. Скачать файлы через `curl -L`:
   - `stitch/raw/<slug>.html`
   - `public/stitch/<slug>.png`
4. Скопировать HTML в runtime:
   - `public/stitch/<slug>.html`
5. Если нужно, применить ручные правки к HTML (как с social login).
6. Добавить wrapper-компонент `src/<PageName>.jsx`.
7. Добавить route в `src/main.jsx`.
8. Обновить этот документ + `README`.
9. Проверить:
   - `npm run build`
   - `docker compose up --build -d --no-deps frontend`
   - `curl -I http://localhost:5173/stitch/<slug>.html`
   - `curl -I http://localhost:5173/<route>`.

---

## 7. Runbook (local)

### Dev

```bash
cd frontend
npm run dev
```

### Production build check

```bash
cd frontend
npm run build
```

### Publish frontend container only

```bash
cd /Users/artemgavrilov/Desktop/Работа/teleMed
docker compose up --build -d --no-deps frontend
```

---

## 8. Known Operational Note

В проекте может возникать конфликт порта `8000` при полном `docker compose up --build -d` из-за backend.  
Для задач только по frontend использовать перезапуск **только frontend**:

```bash
docker compose up --build -d --no-deps frontend
```

---

## 9. Key Files

- Routing entry: `src/main.jsx`
- Native landing: `src/App.jsx`
- Stitch wrappers:
  - `src/DoctorDirectoryWithFiltersPage.jsx`
  - `src/DoctorPublicProfilePage.jsx`
  - `src/PublicQuestionsFeedPage.jsx`
  - `src/LoginDesktopPage.jsx`
  - `src/RegistrationDesktopPage.jsx`
- Runtime stitch assets: `public/stitch/`
- Raw stitch artifacts: `stitch/raw/`
