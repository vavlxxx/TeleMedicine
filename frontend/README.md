# TeleMedicine Frontend

React + Vite frontend for the telemedicine MVP.

## Runtime routes

- `/` - landing
- `/login-desktop-ru` and `/login` - guest login
- `/registration-desktop-ru` and `/register` - guest patient registration
- `/doctor-directory-with-filters-ru` and `/doctors` - public doctor directory
- `/doctor-public-profile-ru?doctor_id=<id>` - public doctor profile
- `/public-questions-feed-ru` and `/questions` - public Q&A feed
- `/account` and `/profile` - protected current-user page
- `/admin-doctor-moderation` and `/admin` - protected admin moderation page
- `/404` - explicit not-found page

Route and UX details are documented in `docs/ROUTES_AND_UX_MAP.md`.

## Run

```bash
npm run dev
```

The default proxy expects backend at `http://localhost:8000`.

## Frontend verification

```bash
npm run test:smoke
npm run lint
npm run build
```

### Current frontend test strategy

- use `node:test` smoke coverage for critical integration contracts in `smoke/`;
- keep the smoke suite focused on API client auth/refresh/logout behavior and routing helpers;
- rely on backend integration tests for API-level end-to-end coverage of auth, moderation, upload, and Q&A flows;
- add a full browser E2E stack only when the UI contracts stabilize enough to justify the maintenance cost.

## Local env

- `VITE_BACKEND_PROXY_TARGET`
- `VITE_API_BASE_URL`

The checked-in example is `frontend/.env.example`.

## Frontend auth model

- access token is kept only in React memory inside `src/auth/AuthContext.jsx`;
- refresh token stays in the backend-managed HttpOnly cookie;
- on app bootstrap the frontend calls `refreshSession()` to restore the session after a reload;
- protected API calls use `credentials: 'include'` and retry once after a `401` by calling refresh;
- logout clears the in-memory access token and relies on backend refresh-session revocation.

## Page architecture

- routing is implemented in `src/main.jsx` with a lightweight custom router in `src/router.jsx`;
- role guards live in `src/RouteGuards.jsx`;
- API contracts are centralized in `src/api/client.js`;
- interactive runtime pages are native React pages, not Stitch iframe wrappers.

Detailed page inventory is in `docs/PAGES_DOCUMENTATION.md`.

## Stitch assets

`public/stitch/` and `stitch/raw/` remain only as visual reference assets for migrated screens. Runtime pages no longer depend on `iframe` wrappers for login, registration, directory, profile, or Q&A.

## Known MVP limitations

- public runtime still exposes only patient registration; doctor registration UI is postponed even though the backend endpoint exists;
- there is no full Playwright/Cypress browser E2E stack yet;
- manual browser QA for the full happy-path and error matrix still has to be repeated before release sign-off.
