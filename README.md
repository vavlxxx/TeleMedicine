# TeleMedicine

Run everything from the repository root:

```bash
docker compose up --build
```

After startup:

- frontend: http://localhost:5173
- backend: http://localhost:8000
- swagger: http://localhost:8000/docs
- postgres: localhost:6432

## Backend implemented

- secure JWT auth: access token + rotating refresh token in HttpOnly cookie
- roles: `admin`, `superuser`, `patient`, `doctor`
- patient and doctor registration
- secure doctor document upload (size/type/extension validation + safe filenames)
- admin doctor verification
- specializations directory with admin CRUD
- Q&A: patient asks, only verified doctor answers

## Bootstrap superuser (dev)

In `backend/.env.docker`:

- `username`: `superadmin`
- `password`: `SuperAdmin!123`

## Environment files

- backend template: `backend/.env.template`
- backend docker env: `backend/.env.docker`

```
CFG_DB__HOST=postgres
CFG_DB__PORT=5432
CFG_DB__USER=postgres
CFG_DB__PASSWORD=postgres
CFG_DB__NAME=telemedicine

CFG_APP__MODE=DEV

CFG_AUTH__SECRET_KEY=dev-only-change-me-super-secret-key-1234567890
CFG_AUTH__COOKIE_SECURE=false
CFG_AUTH__COOKIE_SAMESITE=lax

CFG_CORS__ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

CFG_BOOTSTRAP__SUPERUSER_USERNAME=superadmin
CFG_BOOTSTRAP__SUPERUSER_PASSWORD=SuperAdmin!123
```

- postgres docker env: `backend/.env.postgres`

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=telemedicine
```
