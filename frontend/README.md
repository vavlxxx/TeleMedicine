# TeleMedicine Frontend

React + Vite frontend for the telemedicine landing page.

The first page is implemented as native React JSX (no iframe) in `src/App.jsx` based on the Stitch screen:

- Project: `10685311712153327451`
- Screen: `272e37c4893c43be986b667eb243f046`

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
