# Agent Guide

This repository is a VirtualMedic monorepo:

- `backend/`: FastAPI, SQLAlchemy, Alembic, Poetry, pytest.
- `frontend/`: React, Vite, npm, smoke tests.
- `docker-compose.yaml`: production/server-style compose.
- `local.docker-compose.yaml`: local Docker compose.
- `.github/workflows/build.yaml`: GitHub Actions CI/CD.

Use this guide when starting from a fresh agent dialog.

## Current Operating Rules

- Do not commit or print real secrets.
- Do not use the root server password from chat history. Treat any password shared in chat as exposed and unsafe.
- Real env files are intentionally ignored by git:
  - `backend/.env`
  - `backend/.env.postgres`
  - `backend/.env.docker`
  - `frontend/.env`
- The user works on macOS/zsh. Use `./path`, not Windows `.\path`.
- Prefer local Docker for full-stack checks.
- Do not deploy manually unless the user explicitly asks. Production deploy is handled by GitHub Actions after merge to `main`.

## First Steps In A Fresh Dialog

From the repository root:

```bash
pwd
git status --short --branch
git remote -v
git fetch --all --prune
git status --short --branch
```

If `main` is behind `origin/main`, update it carefully:

```bash
git pull --ff-only
```

If there are local uncommitted changes, do not overwrite them. Either inspect them or preserve them first:

```bash
git diff --stat
git stash push -u -m pre-sync-before-origin-main
git pull --ff-only
```

As of the last setup, there may be an old safety stash:

```bash
git stash list
```

Do not apply or drop a stash unless it is needed for the current task.

## Local Env Files

Local Docker requires:

- `backend/.env`
- `backend/.env.postgres`

If they are missing, create them from templates:

```bash
cp backend/.env.template backend/.env
cp backend/.env.postgres.template backend/.env.postgres
```

For local development, values must match. A known-good local setup is:

`backend/.env`:

```env
CFG_DB__HOST=postgres
CFG_DB__PORT=5432
CFG_DB__USER=postgres
CFG_DB__PASSWORD=postgres
CFG_DB__NAME=virtualmedic

CFG_APP__MODE=DEV

CFG_AUTH__SECRET_KEY=dev-only-change-me-super-secret-key-1234567890
CFG_AUTH__ACCESS_TTL_MINUTES=15
CFG_AUTH__REFRESH_TTL_DAYS=30
CFG_AUTH__COOKIE_SECURE=false
CFG_AUTH__COOKIE_SAMESITE=lax

CFG_CORS__ALLOWED_ORIGINS=["http://localhost","http://127.0.0.1","http://localhost:5173","http://127.0.0.1:5173"]

CFG_UPLOAD__DIRECTORY=/app/uploads/doctor_documents
CFG_UPLOAD__MAX_FILE_SIZE_MB=8
CFG_UPLOAD__MAX_FILES_PER_REQUEST=10

CFG_BOOTSTRAP__SUPERUSER_USERNAME=superadmin
CFG_BOOTSTRAP__SUPERUSER_PASSWORD=SuperAdmin!123
CFG_BOOTSTRAP__SUPERUSER_FIRST_NAME=System
CFG_BOOTSTRAP__SUPERUSER_LAST_NAME=Administrator
```

`backend/.env.postgres`:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=virtualmedic
```

These are local-only development credentials.

## Local Docker Run

Use this on macOS/zsh:

```bash
docker compose -f ./local.docker-compose.yaml up --build -d
```

Check containers:

```bash
docker compose -f ./local.docker-compose.yaml ps
```

Check health:

```bash
curl -i http://localhost/health
curl -I http://localhost/
```

Expected:

- `http://localhost/health` returns `{"status":"ok"}`.
- `http://localhost/` returns frontend `200 OK`.

Open frontend:

```text
http://localhost/
```

Stop local stack:

```bash
docker compose -f ./local.docker-compose.yaml down
```

Full local database reset:

```bash
docker compose -f ./local.docker-compose.yaml down -v
```

Use reset only when the user is fine with deleting local Postgres data.

## Local Non-Docker Run

Backend:

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

For most full-stack work, Docker is the preferred path because it matches the current reverse-proxy setup better.

## Validation Commands

Backend:

```bash
cd backend
poetry run python -m ruff check src tests
poetry run python -m ruff format --check src tests
poetry run python -m pyright
poetry run python -m pytest -v
```

Frontend:

```bash
cd frontend
npm ci
npm run lint
npm run test:smoke
npm run build
```

Docker build checks:

```bash
docker build -t virtualmedic-backend:ci ./backend
docker build -t virtualmedic-frontend:ci ./frontend
```

## Git Workflow

The backend developer configured CI/CD around Pull Requests.

Normal workflow:

```bash
git checkout main
git fetch --all --prune
git pull --ff-only
git checkout -b codex/<short-task-name>
```

Make changes, run relevant checks, then push the branch and open a PR to `main`.

Do not work directly on `main` for feature changes unless the user explicitly asks.

CI runs on PRs into `main`:

- backend ruff
- backend format check
- backend pyright
- backend pytest
- frontend lint
- frontend smoke tests
- frontend build
- backend Docker build
- frontend Docker build

Deploy runs only after push/merge to `main`.

## CI/CD Summary

Workflow file:

```text
.github/workflows/build.yaml
```

Required GitHub Secrets:

- `SSH_PRIVATE_KEY`
- `SSH_KNOWN_HOSTS`
- `SERVER_HOST`
- `SERVER_PORT`
- `SERVER_USER`
- `DEPLOY_PATH`
- `BACKEND_ENV`
- `POSTGRES_ENV`

Server/deploy behavior:

1. GitHub Actions checks out the repository.
2. Connects to the Ubuntu server over SSH.
3. Creates the deploy directory.
4. Syncs repository files with `rsync`.
5. Uploads runtime env files from GitHub Secrets.
6. Runs `docker compose up -d --build --remove-orphans`.
7. Verifies backend health and frontend container response.

Do not put production secrets into tracked files.

## Production Notes

Known server IP:

```text
IPv4: 185.192.247.148
IPv6: 2a03:6f01:1:2::1:de1a
```

Production nginx currently expects domain/cert paths for:

```text
virtualmedic.ru
```

Production compose:

```bash
docker compose up -d --build --remove-orphans
```

Local compose:

```bash
docker compose -f ./local.docker-compose.yaml up --build -d
```

Do not SSH into production or run production commands unless the user specifically requests it.

## Important Files

- `README.md`: main project and CI/CD documentation.
- `local.docker-compose.yaml`: local Docker stack with nginx on port `80`.
- `docker-compose.yaml`: production/server stack with ports `80` and `443`.
- `local.nginx.conf`: local reverse proxy config.
- `nginx.conf`: production reverse proxy config.
- `.github/workflows/build.yaml`: CI/CD pipeline.
- `backend/.env.template`: backend env template.
- `backend/.env.postgres.template`: Postgres env template.
- `frontend/.env.example`: frontend dev env example.

## Common Pitfalls

- The backend developer's command with `.\local.docker-compose.yaml` is Windows syntax. On this Mac use `./local.docker-compose.yaml`.
- If `curl http://localhost` fails inside a restricted sandbox, retry with the required local-network/Docker permission before assuming the app is down.
- `local.docker-compose.yaml` uses port `80`; if port `80` is already occupied, local nginx will fail to start.
- `docker-compose.yaml` is not ideal for local macOS checks because it mounts production Let's Encrypt paths and exposes HTTPS.
- The frontend Docker image serves a production static build through nginx, not `vite dev`.
- Backend and frontend services are not directly published in compose; access goes through root nginx.
