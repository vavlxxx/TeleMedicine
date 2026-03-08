## TeleMedicine Backend (FastAPI)

Secure backend for telemedicine:

- JWT auth (`access` + refresh rotation in HttpOnly cookie)
- roles: `admin`, `superuser`, `patient`, `doctor`
- doctor registration with qualification document uploads
- admin verification workflow for doctors
- specializations directory (admin CRUD)
- patient Q&A where only verified doctors can answer

### Main API

- `POST /api/v1/auth/register/patient`
- `POST /api/v1/auth/register/doctor` (multipart + `documents[]`)
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `PATCH /api/v1/auth/me`
- `POST /api/v1/auth/change-password`
- `GET /api/v1/specializations/`
- `POST/PATCH/DELETE /api/v1/specializations/...` (admin/superuser)
- `GET /api/v1/admin/doctors/pending`
- `PATCH /api/v1/admin/doctors/{doctor_id}/verify`
- `GET /api/v1/questions/`
- `POST /api/v1/questions/` (patient)
- `POST /api/v1/questions/{question_id}/comments` (verified doctor)

### Run

```bash
docker compose up --build
```

Default bootstrap superuser in `backend/.env.docker`:

- `username`: `superadmin`
- `password`: `SuperAdmin!123`

### Migrations

```bash
poetry run alembic upgrade head
```

### Tests

```bash
poetry run python -m pytest
```
