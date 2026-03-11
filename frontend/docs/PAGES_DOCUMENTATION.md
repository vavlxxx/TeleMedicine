# Frontend Pages Documentation

## Scope

This document describes the runtime frontend pages that are actually used by the current MVP build. Interactive pages are native React pages; Stitch exports are kept only as reference assets.

Related docs:

- `docs/ROUTES_AND_UX_MAP.md`
- `docs/FORM_VALIDATION.md`
- `docs/STITCH_MIGRATION_PLAN.md`

## Runtime routing model

- routing entrypoint: `src/main.jsx`
- router implementation: `src/router.jsx`
- access guards: `src/RouteGuards.jsx`
- auth/session state: `src/auth/AuthContext.jsx`

Routes are grouped into:

- `public`
- `guest`
- `protected`

Unknown paths render the explicit `/404` page.

## Page inventory

### Landing

- route: `/`
- file: `src/App.jsx`
- role: public discovery entrypoint
- main actions: go to doctors, questions, login, registration, account/admin

### Login

- routes: `/login-desktop-ru`, `/login`
- file: `src/LoginDesktopPage.jsx`
- role: guest-only
- backend contract: `POST /api/v1/auth/login`
- notes: supports `returnTo`, `registered`, `logged_out`

### Patient registration

- routes: `/registration-desktop-ru`, `/register`
- file: `src/RegistrationDesktopPage.jsx`
- role: guest-only
- backend contract: `POST /api/v1/auth/register/patient`
- notes: redirects to login with `registered=1`

### Current user account

- routes: `/account`, `/profile`
- file: `src/AccountPage.jsx`
- role: protected
- backend contracts:
  - `GET /api/v1/auth/me`
  - `PATCH /api/v1/auth/me`
  - `POST /api/v1/auth/change-password`
  - `POST /api/v1/auth/logout`
  - `GET /api/v1/auth/me/documents`
  - `POST /api/v1/doctors/me/documents`

### Admin moderation

- routes: `/admin-doctor-moderation`, `/admin`
- file: `src/AdminDoctorModerationPage.jsx`
- role: protected `admin/superuser`
- backend contracts:
  - `GET /api/v1/admin/doctors/pending`
  - `GET /api/v1/admin/doctors/{doctor_id}`
  - `PATCH /api/v1/admin/doctors/{doctor_id}/verify`
  - `GET /api/v1/admin/documents/{document_id}`

### Doctor directory

- routes: `/doctor-directory-with-filters-ru`, `/doctors`
- file: `src/DoctorDirectoryWithFiltersPage.jsx`
- role: public
- backend contracts:
  - `GET /api/v1/doctors/`
  - `GET /api/v1/specializations/`

### Doctor public profile

- route: `/doctor-public-profile-ru?doctor_id=<id>`
- file: `src/DoctorPublicProfilePage.jsx`
- role: public
- backend contract: `GET /api/v1/doctors/{doctor_id}`
- note: only public doctor fields are rendered; qualification documents stay hidden

### Public questions feed

- routes: `/public-questions-feed-ru`, `/questions`
- file: `src/PublicQuestionsFeedPage.jsx`
- role: public
- backend contracts:
  - `GET /api/v1/questions/`
  - `GET /api/v1/questions/{question_id}`
  - `POST /api/v1/questions/`
  - `POST /api/v1/questions/{question_id}/comments`
- notes:
  - patient can create a question inline;
  - only verified doctors can answer;
  - login/registration CTAs preserve `returnTo`.

### Not found

- route: `/404`
- file: `src/NotFoundPage.jsx`
- role: public fallback page

## Native React migration status

The following former Stitch-first screens are now fully native React runtime pages:

- `login-desktop-ru`
- `registration-desktop-ru`
- `doctor-directory-with-filters-ru`
- `doctor-public-profile-ru`
- `public-questions-feed-ru`

No runtime `iframe` wrappers remain for these screens.

## Stitch asset policy

- `public/stitch/` keeps exported HTML/PNG reference assets.
- `stitch/raw/` keeps raw Stitch artifacts.
- these files are not part of runtime routing or runtime interactivity.

## Operational checks

Current frontend verification commands:

```bash
cd frontend
npm run test:smoke
npm run lint
npm run build
```

For full stack verification from the repository root:

```bash
docker compose up --build
```
