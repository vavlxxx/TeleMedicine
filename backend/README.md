## TeleMedicine Backend

FastAPI backend for the telemedicine MVP.

### Implemented backend scope

- patient and doctor registration;
- login, refresh rotation, logout, current user profile, profile update, password change;
- role model: `patient`, `doctor`, `admin`, `superuser`;
- doctor qualification document storage with upload validation;
- admin moderation queue and doctor verification toggle;
- public doctor directory/profile and Q&A endpoints.

### Main API

- `POST /api/v1/auth/register/patient`
- `POST /api/v1/auth/register/doctor`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `PATCH /api/v1/auth/me`
- `GET /api/v1/auth/me/documents`
- `POST /api/v1/auth/change-password`
- `GET /api/v1/specializations/`
- `POST /api/v1/specializations/`
- `PATCH /api/v1/specializations/{specialization_id}`
- `DELETE /api/v1/specializations/{specialization_id}`
- `GET /api/v1/doctors/`
- `GET /api/v1/doctors/{doctor_id}`
- `POST /api/v1/doctors/me/documents`
- `GET /api/v1/admin/doctors/pending`
- `GET /api/v1/admin/doctors/{doctor_id}`
- `PATCH /api/v1/admin/doctors/{doctor_id}/verify`
- `GET /api/v1/admin/documents/{document_id}`
- `GET /api/v1/questions/`
- `GET /api/v1/questions/{question_id}`
- `POST /api/v1/questions/`
- `POST /api/v1/questions/{question_id}/comments`

### Local run

From the repository root:

```bash
docker compose up --build
```

Standalone backend app in Docker Compose:

- backend: `http://localhost:8000`
- health: `http://localhost:8000/health`

### Migrations

```bash
poetry run alembic upgrade head
```

### Test run

Preferred reproducible command from the repository root:

```bash
docker compose run --rm backend-test poetry run python -m pytest
```

This uses the dedicated `backend-test` image stage with dev dependencies and runs the suite against SQLite test storage.

### Backend env variables

Local/dev setup uses:

- `CFG_DB__HOST`
- `CFG_DB__PORT`
- `CFG_DB__USER`
- `CFG_DB__PASSWORD`
- `CFG_DB__NAME`
- `CFG_APP__MODE`
- `CFG_AUTH__SECRET_KEY`
- `CFG_AUTH__ACCESS_TTL_MINUTES`
- `CFG_AUTH__REFRESH_TTL_DAYS`
- `CFG_AUTH__COOKIE_SECURE`
- `CFG_AUTH__COOKIE_SAMESITE`
- `CFG_AUTH__COOKIE_DOMAIN`
- `CFG_CORS__ALLOWED_ORIGINS`
- `CFG_UPLOAD__DIRECTORY`
- `CFG_UPLOAD__MAX_FILE_SIZE_MB`
- `CFG_UPLOAD__MAX_FILES_PER_REQUEST`
- `CFG_UPLOAD__ALLOWED_EXTENSIONS`
- `CFG_UPLOAD__ALLOWED_MIME_TYPES`
- `CFG_BOOTSTRAP__SUPERUSER_USERNAME`
- `CFG_BOOTSTRAP__SUPERUSER_PASSWORD`
- `CFG_BOOTSTRAP__SUPERUSER_FIRST_NAME`
- `CFG_BOOTSTRAP__SUPERUSER_LAST_NAME`

See `backend/.env.template` for the local starting point.

### Auth contract

- login returns `AuthTokenResponseDTO` with `access_token`, `expires_in`, `token_type`, and current `user`;
- refresh rotates the refresh session, revokes the previous one, and returns a new access token;
- logout revokes the active refresh session if present and clears the cookie;
- access token is expected in `Authorization: Bearer ...`;
- refresh token is expected only in the cookie named by `CFG_AUTH__REFRESH_COOKIE_NAME` (default `refresh_token`).

### Doctor registration flow

1. Admin creates specializations.
2. Doctor sends multipart registration with identity fields, `specialization_ids`, and `documents`.
3. Backend validates each file by extension, MIME type, count, and size.
4. Doctor is created with `is_verified_doctor=false`.
5. Admin reviews the uploaded documents and toggles verification.

### Admin verification flow

1. `GET /api/v1/admin/doctors/pending` returns unverified doctors with qualification document metadata.
2. `GET /api/v1/admin/doctors/{doctor_id}` returns the moderation detail DTO.
3. `GET /api/v1/admin/documents/{document_id}` streams the stored document file.
4. `PATCH /api/v1/admin/doctors/{doctor_id}/verify` toggles `is_verified_doctor`.
5. Verification is rejected when a doctor has no uploaded qualification documents.

### Production guardrails

When `CFG_APP__MODE=PROD`, backend config now enforces:

- strong non-dev secret key;
- `CFG_AUTH__COOKIE_SECURE=true`;
- non-empty non-localhost CORS origins;
- disabled docs/openapi endpoints.
