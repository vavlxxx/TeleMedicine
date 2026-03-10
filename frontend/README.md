# TeleMedicine Frontend

React + Vite frontend for the telemedicine landing page.

Full pages documentation:

- `docs/PAGES_DOCUMENTATION.md`

The first page is implemented as native React JSX (no iframe) in `src/App.jsx` based on the Stitch screen:

- Project: `10685311712153327451`
- Screen: `272e37c4893c43be986b667eb243f046`

Independent Stitch-based page:

- `Doctor Directory with Filters (RU)` (`9871202d4c1b4b46a0fb6bb7af520bdf`)
- Route: `/doctor-directory-with-filters-ru`
- Hosted export files:
  - `public/stitch/doctor-directory-with-filters-ru.html`
  - `public/stitch/doctor-directory-with-filters-ru.png`

Independent Stitch-based page:

- `Doctor Public Profile (RU)` (`d4ff542a39c448f9803dd23cc14d2a32`)
- Route: `/doctor-public-profile-ru`
- Hosted export files:
  - `public/stitch/doctor-public-profile-ru.html`
  - `public/stitch/doctor-public-profile-ru.png`

Independent Stitch-based page:

- `Public Questions Feed (RU)` (`a179243b938345b2a10fb4d7608e0a5e`)
- Route: `/public-questions-feed-ru`
- Hosted export files:
  - `public/stitch/public-questions-feed-ru.html`
  - `public/stitch/public-questions-feed-ru.png`

Independent Stitch-based page:

- `Вход в систему (Desktop)` (`14fe5d2debf248baabc172593526281e`)
- Route: `/login-desktop-ru`
- Hosted export files:
  - `public/stitch/login-desktop-ru.html`
  - `public/stitch/login-desktop-ru.png`
- Adjustment:
  - removed extra `Войти через` social login block from the stitched HTML

Independent Stitch-based page:

- `Регистрация (Desktop)` (`5f926a656fa04515b7c0a195cbca6953`)
- Route: `/registration-desktop-ru`
- Hosted export files:
  - `public/stitch/registration-desktop-ru.html`
  - `public/stitch/registration-desktop-ru.png`

## Run

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Stitch Screen Sync

Download Stitch screen payload + hosted HTML/PNG into this project:

```bash
STITCH_API_KEY="<your-api-key>" npm run fetch:stitch
```

Output files:

- `stitch/raw/screen-code-response.json`
- `stitch/raw/screen-image-response.json`
- `stitch/raw/telehealth-landing-ru.html`
- `stitch/raw/hosted-urls.txt`
- `public/stitch/telehealth-landing-ru.html`
- `public/stitch/telehealth-landing-ru.png`
