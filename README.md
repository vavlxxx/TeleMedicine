# VirtualMedic

VirtualMedic — это монорепозиторий, в котором находятся:

- `backend/` на FastAPI + SQLAlchemy + Alembic
- `frontend/` на React + Vite
- `docker-compose.yaml` для локального и серверного запуска
- `nginx.conf` как внешний reverse proxy
- `.github/workflows/build.yaml` для CI/CD в GitHub Actions

## Структура репозитория

```text
.
|-- .github/workflows/build.yaml
|-- backend/
|   |-- src/
|   |-- tests/
|   |-- Dockerfile
|   |-- pyproject.toml
|   |-- .env.template
|   `-- .env.postgres.template
|-- frontend/
|   |-- src/
|   |-- public/
|   |-- smoke/
|   |-- docs/
|   |-- Dockerfile
|   |-- nginx.conf
|   |-- .env.example
|   `-- .env.production.example
|-- docker-compose.yaml
|-- nginx.conf
`-- README.md
```

## Архитектура запуска

Во внешний мир публикуется только корневой `nginx`.

Внутри Docker-сети работают:

- `postgres` на `5432`
- `backend` на `8000`
- `frontend`, который отдаёт статическую production-сборку на `80`
- корневой `nginx` на `80` и `443`

Схема трафика:

- `https://your-domain/` -> корневой `nginx` -> контейнер frontend
- `https://your-domain/api/...` -> корневой `nginx` -> контейнер backend
- `https://your-domain/health` -> корневой `nginx` -> backend `/health`

Это означает:

- PostgreSQL не опубликован наружу на хост
- backend не опубликован напрямую на хост
- frontend не опубликован напрямую на хост
- frontend внутри Docker работает как production static build, а не как `vite dev`

## Env-файлы

Проект использует разные env-файлы для backend, PostgreSQL и локальной разработки frontend.

Реальные env-файлы нельзя коммитить в git. В репозитории хранятся только шаблоны и примеры.

### 1. `backend/.env`

Шаблон: `backend/.env.template`

Создание:

```bash
cp backend/.env.template backend/.env
```

PowerShell:

```powershell
Copy-Item backend/.env.template backend/.env
```

Этот файл настраивает само FastAPI-приложение.

Обязательные значения для замены:

- `CFG_DB__USER`
- `CFG_DB__PASSWORD`
- `CFG_AUTH__SECRET_KEY`

Важные поля:

- `CFG_DB__HOST=postgres` для Docker runtime
- `CFG_APP__MODE=DEV` для локальной разработки
- `CFG_APP__MODE=PROD` для production
- `CFG_CORS__ALLOWED_ORIGINS` в production должен содержать реальный домен frontend
- `CFG_AUTH__COOKIE_SECURE=true` обязателен в production

Для production нужно взять тот же шаблон, заменить небезопасные значения и затем сохранить полное содержимое файла в GitHub Secret `BACKEND_ENV`.

### 2. `backend/.env.postgres`

Шаблон: `backend/.env.postgres.template`

Создание:

```bash
cp backend/.env.postgres.template backend/.env.postgres
```

PowerShell:

```powershell
Copy-Item backend/.env.postgres.template backend/.env.postgres
```

Этот файл настраивает контейнер PostgreSQL.

Обязательные значения для замены:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`

Эти значения должны совпадать с DB-настройками из `backend/.env`.

Для CI/CD содержимое этого файла нужно положить в GitHub Secret `POSTGRES_ENV`.

### 3. `frontend/.env`

Шаблон: `frontend/.env.example`

Этот файл нужен только если frontend запускается локально через `npm run dev`:

```bash
cp frontend/.env.example frontend/.env
```

PowerShell:

```powershell
Copy-Item frontend/.env.example frontend/.env
```

Назначение:

- локальный Vite dev server
- proxy `/api` запросов в локальный backend

Значения в примере по умолчанию:

- `VITE_BACKEND_PROXY_TARGET=http://localhost:8000`
- `VITE_API_BASE_URL=/api/v1`

### 4. `frontend/.env.production.example`

Пример: `frontend/.env.production.example`

Этот файл нужен как reference для локальных production-style сборок frontend вне Docker.

Текущий production Docker image frontend не требует runtime env-файла, потому что собранный bundle по умолчанию использует `VITE_API_BASE_URL=/api/v1` и затем отдаётся как статические файлы через `nginx`.

Именно поэтому текущий deploy в GitHub Actions использует только:

- `BACKEND_ENV`
- `POSTGRES_ENV`

и не требует `FRONTEND_ENV`.

## Локальный запуск через Docker

Сначала подготовь env-файлы:

- создай `backend/.env`
- создай `backend/.env.postgres`

После этого из корня репозитория:

```bash
docker compose up --build
```

Проверка сервисов:

```bash
curl http://localhost/health
```

Открыть в браузере:

- `http://localhost/` — frontend
- `http://localhost/docs` — Swagger в режиме `DEV`

Остановка:

```bash
docker compose down
```

Полный сброс с удалением volume базы:

```bash
docker compose down -v
```

## Локальный запуск без Docker

### Backend

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

### Frontend

Подготовь `frontend/.env`, затем:

```bash
cd frontend
npm ci
npm run dev
```

## Проверки и валидация

### Backend

```bash
cd backend
poetry run python -m ruff check src tests
poetry run python -m ruff format --check src tests
poetry run python -m pyright
poetry run python -m pytest -v
```

### Frontend

```bash
cd frontend
npm ci
npm run lint
npm run test:smoke
npm run build
```

### Docker

```bash
docker build -t virtualmedic-backend ./backend
docker build -t virtualmedic-frontend ./frontend
```

## CI/CD в GitHub Actions

Файл workflow: `.github/workflows/build.yaml`

Триггеры:

- `pull_request` в `main`
- `push` в `main`

### Что запускается на Pull Request

- backend-проверки: `ruff`, `ruff format --check`, `pyright`, `pytest`
- frontend-проверки: `lint`, `test:smoke`, `build`
- проверка Docker build backend image
- проверка Docker build frontend image

### Что запускается на Push в `main`

Сначала проходят те же CI-проверки. Если они успешны, GitHub Actions делает deploy на Ubuntu-сервер:

1. подключается по SSH
2. создаёт deploy-директорию, если её ещё нет
3. синхронизирует файлы репозитория через `rsync`
4. загружает `backend/.env` и `backend/.env.postgres` из GitHub Secrets
5. запускает `docker compose up -d --build --remove-orphans`
6. проверяет backend health и ответ frontend внутри контейнеров

### Какие GitHub Secrets нужны

- `SSH_PRIVATE_KEY`
- `SSH_KNOWN_HOSTS`
- `SERVER_HOST`
- `SERVER_PORT`
- `SERVER_USER`
- `DEPLOY_PATH`
- `BACKEND_ENV`
- `POSTGRES_ENV`

### Требования к серверу

На Ubuntu-сервере уже должны быть:

- `docker`
- `docker compose`
- SSH-доступ по ключу для deploy-пользователя
- директория проекта, совпадающая с `DEPLOY_PATH`
- валидные Let's Encrypt файлы, если сохраняется текущая схема с mount в корневом `nginx.conf`:
  - `/etc/letsencrypt`
  - `/var/lib/letsencrypt`

У deploy-пользователя должны быть права на выполнение Docker-команд.

## Как правильно заполнять GitHub Secrets

### `BACKEND_ENV`

Возьми `backend/.env.template`, замени placeholder-значения на production-значения, затем скопируй полное содержимое файла в GitHub Secret `BACKEND_ENV`.

Минимальные production-настройки:

- `CFG_APP__MODE=PROD`
- сильный `CFG_AUTH__SECRET_KEY`
- `CFG_AUTH__COOKIE_SECURE=true`
- production-домен в `CFG_CORS__ALLOWED_ORIGINS`
- отключённые docs в production:
  - `CFG_APP__DOCS_URL=`
  - `CFG_APP__REDOC_URL=`
  - `CFG_APP__OPENAPI_URL=`

### `POSTGRES_ENV`

Возьми `backend/.env.postgres.template`, замени placeholder-значения и затем скопируй полное содержимое файла в GitHub Secret `POSTGRES_ENV`.

### `SSH_KNOWN_HOSTS`

Сгенерируй значение со своей рабочей машины:

```bash
ssh-keyscan -p <server_port> <server_host>
```

Результат нужно сохранить в GitHub Secret `SSH_KNOWN_HOSTS`.

## Примечания по Production

Текущая схема деплоя корректна для этого репозитория в его текущем состоянии, потому что:

- backend и frontend собираются как отдельные Docker images
- frontend теперь работает как статический production bundle через `nginx`
- корневой `nginx` проксирует `/` во frontend, а `/api` в backend
- deploy в GitHub Actions согласован с `docker-compose.yaml`
- health-check после deploy проверяет и backend, и frontend контейнеры

Текущие ограничения:

- deploy выполняется in-place, без blue-green схемы
- нет автоматического rollback
- образы собираются на сервере во время deploy, а не публикуются в registry
- предполагается, что SSL-сертификаты уже существуют на сервере

## Итог по структуре проекта

Структура репозитория в целом логична для небольшого монорепозитория:

- `backend/` содержит код приложения, миграции и тесты
- `frontend/` содержит код приложения, smoke-тесты и документацию по UI
- инфраструктурные файлы вынесены в корень репозитория
- CI/CD теперь соответствует реальной production-схеме запуска

Основное структурное расхождение, которое было раньше, касалось frontend runtime в Docker:

- раньше: `vite dev` внутри Docker
- сейчас: production static build через `nginx`

Это расхождение устранено.
