# TeleMedicine MVP

Monorepo with a FastAPI backend and a React/Vite frontend for the first telemedicine MVP.

## What is implemented

- patient registration and login;
- JWT auth with in-memory access token on the frontend and rotating refresh token in an HttpOnly cookie;
- current-user profile, profile update, password change, logout;
- doctor registration backend flow with qualification document upload;
- admin/superuser moderation queue for doctor verification;
- public doctor directory and public doctor profile;
- public Q&A feed where patients create questions and only verified doctors can answer.

## Repository layout

- `backend/` - FastAPI application, migrations, pytest suite.
- `frontend/` - React/Vite SPA with public, guest, protected, and admin routes.
- `docs/PRODUCTION_RUNBOOK.md` - production deployment checklist.
- `docs/RELEASE_READINESS.md` - acceptance summary, deferred tasks, and release limitations.

## Local start

Run from the repository root:

```bash
docker compose up --build
```

Published services:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`
- health: `http://localhost:8000/health`
- postgres: `localhost:6432`

Bootstrap superuser from `backend/.env.docker`:

- username: `superadmin`
- password: `SuperAdmin!123`

## Verification commands

Backend tests:

```bash
docker compose run --rm backend-test poetry run python -m pytest
```

Frontend smoke, lint, build:

```bash
cd frontend
npm run test:smoke
npm run lint
npm run build
```

## Local development env

Backend local env is documented in `backend/.env.template`. The current local/Docker setup uses:

- `CFG_DB__HOST`, `CFG_DB__PORT`, `CFG_DB__USER`, `CFG_DB__PASSWORD`, `CFG_DB__NAME`
- `CFG_APP__MODE`
- `CFG_AUTH__SECRET_KEY`
- `CFG_AUTH__ACCESS_TTL_MINUTES`
- `CFG_AUTH__REFRESH_TTL_DAYS`
- `CFG_AUTH__COOKIE_SECURE`
- `CFG_AUTH__COOKIE_SAMESITE`
- `CFG_CORS__ALLOWED_ORIGINS`
- `CFG_UPLOAD__MAX_FILE_SIZE_MB`
- `CFG_UPLOAD__MAX_FILES_PER_REQUEST`
- `CFG_BOOTSTRAP__SUPERUSER_USERNAME`
- `CFG_BOOTSTRAP__SUPERUSER_PASSWORD`
- `CFG_BOOTSTRAP__SUPERUSER_FIRST_NAME`
- `CFG_BOOTSTRAP__SUPERUSER_LAST_NAME`

Frontend local env:

- `VITE_BACKEND_PROXY_TARGET`
- `VITE_API_BASE_URL`

## Auth flow

1. Frontend calls `POST /api/v1/auth/login`.
2. Backend returns `access_token` in JSON and sets a rotating `refresh_token` cookie with `HttpOnly`.
3. Frontend stores the access token only in React memory, never in `localStorage` or `sessionStorage`.
4. On page load and on `401`, frontend tries `POST /api/v1/auth/refresh` with `credentials: include`.
5. `POST /api/v1/auth/logout` revokes the refresh session and clears the cookie; frontend drops the in-memory access token.

## Doctor registration and moderation

- doctor self-registration is implemented on the backend as multipart `POST /api/v1/auth/register/doctor`;
- qualification documents are validated by extension, MIME type, file count, and file size;
- admin moderation UI is available at `/admin-doctor-moderation` for `admin` and `superuser`;
- admins use `/api/v1/admin/doctors/pending`, `/api/v1/admin/doctors/{doctor_id}`, `/api/v1/admin/doctors/{doctor_id}/verify`, and `/api/v1/admin/documents/{document_id}`;
- public doctor endpoints never expose qualification documents.

## Production notes

- `PROD` mode rejects weak/dev secret keys.
- `PROD` mode requires `CFG_AUTH__COOKIE_SECURE=true`.
- `PROD` mode rejects localhost CORS origins.
- `PROD` mode requires API docs/OpenAPI endpoints to be disabled.

Full deployment steps are in `docs/PRODUCTION_RUNBOOK.md`.

## Current MVP limitations

- doctor self-registration UI is postponed; the backend contract is ready, but the public runtime exposes only patient registration;
- there is no full browser E2E stack yet; frontend coverage is currently smoke-level plus backend integration tests;
- manual browser QA for all user journeys still has to be repeated before a public release.
