# TeleMedicine MVP

TeleMedicine MVP — это монорепозиторий с backend на FastAPI и frontend на React/Vite.

## Состав проекта

- `backend/` — API, бизнес-логика, модели, миграции, тесты
- `frontend/` — пользовательский интерфейс и smoke-тесты
- `docker-compose.yaml` — локальный запуск сервисов
- `nginx.conf` — reverse proxy между браузером, frontend и backend
- `docs/ARCHITECTURE.md` — краткая схема архитектуры
- `docs/PRODUCTION_RUNBOOK.md` — краткий runbook для production

## Что умеет приложение

- регистрация и логин пациента
- регистрация врача с загрузкой подтверждающих документов
- refresh/access JWT-аутентификация
- профиль пользователя и смена пароля
- каталог врачей и публичный профиль врача
- публичная лента вопросов
- ответы на вопросы от подтверждённых врачей
- административная модерация врачей

## Архитектура запуска

Во внешний мир опубликован только `nginx` на порту `80`.

Внутри сети Docker работают:

- `postgres` — `5432`
- `backend` — `8000`
- `frontend` — `5173`

Следствия:

- PostgreSQL не доступен с хоста напрямую
- backend не доступен с хоста напрямую
- frontend не доступен с хоста напрямую как отдельный сервис
- весь внешний HTTP-трафик идёт только через `nginx`

Основные маршруты:

- `http://localhost/` → frontend
- `http://localhost/api/...` → backend
- `http://localhost/health` → healthcheck backend
- `http://localhost/docs` → Swagger в режиме `DEV`

## Текущее состояние и найденные проблемы

### Миграции

Подозрение про отсутствие миграций для текущих таблиц не подтвердилось.

Текущие таблицы backend:

- `users`
- `refresh_sessions`
- `specializations`
- `doctor_specializations`
- `doctor_qualification_documents`
- `questions`
- `question_comments`

Они уже создаются миграцией `backend/src/migrations/versions/2025_12_29_1832-8093419d4e91_removed_unused_fields.py`.

При этом есть две реальные проблемы в миграционном слое:

1. Ревизия `backend/src/migrations/versions/2026_02_15_2152-2094603e316e_added_basic_role_model.py` пустая. Это не ломает запуск, но это плохой сигнал по дисциплине миграций.
2. Первая миграция была неустойчива к уже существующему enum `user_role` в PostgreSQL. Это исправлено через `checkfirst=True`.

### Конфигурация

Исправленные проблемы:

1. Локальные `.env` файлы могли попадать внутрь Docker image. Это небезопасно и даёт расхождение между ожидаемым runtime и тем, что реально собрано. Исправлено через `backend/.dockerignore` и `frontend/.dockerignore`.
2. `CFG_CORS__ALLOWED_ORIGINS` в текущей модели настроек должен задаваться как JSON-массив. Формат строки через запятую здесь не работает стабильно из-за поведения `pydantic-settings` на вложенных полях.
3. Загрузки должны храниться на хосте, а не внутри эфемерной файловой системы контейнера. Сейчас они сохраняются в `backend/uploads`.
4. Frontend внутри Docker всё ещё запускается через `vite dev`. Для локальной разработки это нормально, для production — нет.

### Тестовый контур

Есть один важный архитектурный нюанс:

- backend-тесты создают схему напрямую через ORM (`Base.metadata.create_all()`), а не через Alembic
- поэтому будущий разрыв между моделями и миграциями может не быть замечен тестами автоматически

Это не блокирует текущую работу, но это реальный технический долг.

## Подготовка окружения

### 1. Backend env

Создай локальный файл `backend/.env` на основе шаблона:

```bash
cp backend/.env.template backend/.env
```

PowerShell:

```powershell
Copy-Item backend/.env.template backend/.env
```

Обязательные поля:

- `CFG_DB__USER`
- `CFG_DB__PASSWORD`
- `CFG_AUTH__SECRET_KEY`

Для Docker-режима backend должен ходить в PostgreSQL по адресу `postgres:5432`.

### 2. PostgreSQL env

Создай локальный файл `backend/.env.postgres`:

```bash
cp backend/.env.postgres.template backend/.env.postgres
```

PowerShell:

```powershell
Copy-Item backend/.env.postgres.template backend/.env.postgres
```

Значения `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` должны совпадать с backend-настройками подключения к базе.

### 3. Frontend env

Создай локальный файл `frontend/.env`:

```bash
cp frontend/.env.example frontend/.env
```

PowerShell:

```powershell
Copy-Item frontend/.env.example frontend/.env
```

## Локальный запуск приложения

Из корня проекта:

```bash
docker compose up --build
```

Проверка после старта:

```bash
curl http://localhost/health
```

В браузере:

- главная страница: `http://localhost/`
- Swagger: `http://localhost/docs`

Остановка:

```bash
docker compose down
```

Полная очистка с томами базы:

```bash
docker compose down -v
```

## Работа с приложением

### Основной пользовательский сценарий

1. Открыть `http://localhost/`
2. Зарегистрировать пациента или войти существующим пользователем
3. После логина frontend хранит access token в памяти, а refresh token остаётся в cookie
4. При перезагрузке страницы frontend восстанавливает сессию через `/api/v1/auth/refresh`
5. Публичные страницы каталога врачей и вопросов доступны без логина
6. Административные маршруты доступны только пользователям с ролью `admin` или `superuser`

### Документы врачей

Загрузки сохраняются в:

- внутри контейнера: `/app/uploads/doctor_documents`
- на хосте: `backend/uploads/doctor_documents`

Это означает, что файлы не пропадут при пересоздании контейнера backend, пока не удалена папка `backend/uploads`.

### Основные API-группы

#### Auth

- `POST /api/v1/auth/register/patient`
- `POST /api/v1/auth/register/doctor`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `PATCH /api/v1/auth/me`
- `POST /api/v1/auth/change-password`

#### Doctors

- `GET /api/v1/doctors/`
- `GET /api/v1/doctors/{doctor_id}`
- `POST /api/v1/doctors/me/documents`

#### Admin

- `GET /api/v1/admin/doctors/pending`
- `GET /api/v1/admin/doctors/{doctor_id}`
- `PATCH /api/v1/admin/doctors/{doctor_id}/verify`
- `GET /api/v1/admin/documents/{document_id}`

#### Questions

- `GET /api/v1/questions/`
- `GET /api/v1/questions/{question_id}`
- `POST /api/v1/questions/`
- `POST /api/v1/questions/{question_id}/comments`

## Запуск без Docker

### Backend

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

## Тесты и локальная валидация

### Backend

```bash
cd backend
poetry run pytest -v
```

### Frontend

```bash
cd frontend
npm run lint
npm run test:smoke
npm run build
```

Если нужно прогнать backend-тесты внутри контейнера, можно временно заменить команду сервиса `backend` на `poetry run pytest -v`.

## Pre-commit и проверки перед push

В проекте используется `.pre-commit-config.yaml`.

### Что проверяется на commit

На стадии `pre-commit` выполняются:

- `trailing-whitespace`
- `end-of-file-fixer`
- `check-yaml`
- `check-added-large-files`
- `ruff check` для backend
- `ruff format` для backend
- `pyright` для backend

### Что проверяется перед push

На стадии `pre-push` выполняются:

- `pytest -v` для backend
- `npm run lint` для frontend
- `npm run test:smoke` для frontend

Это соответствует требованию проверять тесты перед отправкой в репозиторий.

### Установка pre-commit

Системный `pre-commit` не обязателен. В этой конфигурации удобнее использовать его из backend venv:

```bash
cd backend
poetry install
poetry run python -m pre_commit install
poetry run python -m pre_commit install --hook-type pre-push
```

Из корня репозитория можно запускать так:

```bash
poetry -C backend run python -m pre_commit run --all-files
poetry -C backend run python -m pre_commit run --all-files --hook-stage pre-push
```

### Нужен ли глобальный eslint

Нет, не нужен.

Причина:

- hook запускает `npm --prefix frontend run lint`
- `npm run` использует локальный `eslint` из `frontend/node_modules`
- достаточно, чтобы в `frontend` были установлены зависимости через `npm ci`

### Есть ли смысл держать JS в pre-commit

Да, смысл есть, но не на стадии `pre-commit`, а на стадии `pre-push`.

Причина:

- frontend в этом репозитории — полноценная часть продукта
- lint и smoke-тесты frontend важны не меньше backend-проверок
- но запускать их на каждый commit неудобно и медленно

Поэтому выбран практичный баланс:

- Python-проверки — на `pre-commit`
- frontend lint и smoke — на `pre-push`

Если команда маленькая и frontend меняется редко, можно оставить только Python hooks локально, а JS полностью доверить CI. Но для этого проекта текущая схема выглядит разумнее.

## CI/CD: что делать дальше

Текущая docker-схема подходит для локального запуска и staging-подготовки.

Для production нужно сделать ещё два шага:

1. собирать frontend как статический bundle
2. отдавать frontend из `nginx`, а не через `vite dev`

Минимальный pipeline CI/CD должен выполнять:

1. `pre-commit run --all-files`
2. backend tests
3. frontend lint
4. frontend smoke tests
5. frontend build
6. docker build
7. deploy

## Рудиментарные файлы

Файл `INTEGRATION_TODO.md` не используется в рабочем контуре и не нужен для итоговой сборки. В текущем состоянии репозитория его нет, и дальше использовать такие файлы не нужно.

## Полезные файлы

- `README.md`
- `docker-compose.yaml`
- `nginx.conf`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `backend/.env.template`
- `backend/.env.postgres.template`
- `frontend/.env.example`
- `docs/ARCHITECTURE.md`
- `docs/PRODUCTION_RUNBOOK.md`
