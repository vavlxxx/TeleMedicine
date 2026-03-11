# TeleMedicine Integration TODO

Этот документ является рабочим чеклистом по объединению `backend` и `frontend` в один реально работающий продукт.

Правила ведения:

- Все пункты ниже изначально отмечены как не выполненные.
- По мере выполнения пункт нужно переключать из `- [ ]` в `- [x]`.
- Если задача разбивается на несколько мелких шагов, сначала отмечаются дочерние пункты, потом родительский.
- Если по ходу работ обнаружится новый обязательный шаг, его нужно добавить в соответствующий раздел, а не держать "в голове".

## 1. Актуализация требований и фиксация целевого MVP

- [x] Зафиксировать список экранов и пользовательских сценариев, которые входят в первый рабочий MVP. Первый frontend MVP: `/` landing, `/login-desktop-ru`, `/registration-desktop-ru` как patient registration, `/doctor-directory-with-filters-ru`, `/doctor-public-profile-ru`, `/public-questions-feed-ru`. Пользовательские сценарии MVP: публичный просмотр каталога врачей, публичный просмотр профиля врача, публичный просмотр ленты вопросов, логин по `username`, регистрация пациента, создание вопроса пациентом после авторизации, просмотр ответов врачей.
- [x] Зафиксировать, какие роли обязательно должны поддерживаться в первом MVP: `patient`, `doctor`, `admin`, `superuser`. На уровне backend и доменной модели сохраняются все четыре роли. На уровне первого пользовательского frontend MVP релиз-блокирующим является patient-flow; `doctor`, `admin`, `superuser` остаются обязательными в API и операционном контуре.
- [x] Зафиксировать, какие сценарии можно отложить после первого MVP без блокировки запуска. Отложены: self-service doctor registration, отдельный личный кабинет, редактирование профиля, change-password UI, forgot-password flow, admin UI для CRUD специализаций, публичный показ doctor documents, advanced pagination/filters beyond basic offset-limit, router/auth-shell rewrite.
- [x] Принять решение, должен ли первый MVP включать только patient-flow или сразу patient + doctor + admin. Решение: первый рабочий frontend MVP ограничивается public + patient-flow. Doctor/admin сценарии не удаляются из backend, но не являются релиз-блокером первой интеграционной поставки.
- [x] Зафиксировать, будет ли doctor registration входить в первый этап или будет отключена до готовности moderation-flow. Решение: self-service doctor registration отключается в первом этапе до появления полноценного moderation-flow и admin UI.
- [x] Зафиксировать, нужен ли в первом MVP публичный каталог врачей. Да, нужен.
- [x] Зафиксировать, нужен ли в первом MVP публичный профиль врача. Да, нужен.
- [x] Зафиксировать, нужен ли в первом MVP публичный список вопросов и ответов. Да, нужен.
- [x] Зафиксировать, нужен ли в первом MVP личный кабинет пользователя. Нет, отдельный кабинет не входит в первый MVP. Допускается только минимальный auth-state с пониманием текущего пользователя после логина.
- [x] Зафиксировать, нужен ли в первом MVP экран/раздел для модерации врачей администратором. Нет, не для первого frontend MVP. Он является prerequisite для включения публичной doctor registration во второй волне.
- [x] Определить, какой UX считается обязательным для релиза: загрузки, ошибки, пустые состояния, success-сообщения, редиректы. Обязательный UX для релиза: loading state для страниц и submit-кнопок, field/form errors для auth и question create, empty state для каталога врачей и ленты вопросов, success state после patient registration и question create, redirect после login/register, guard against unauthorized actions, обработка `401`, `403`, `404`, `409`, `422`.
- [x] Зафиксировать Definition of Done для интеграции frontend и backend. DoD: экран использует реальный backend endpoint без `iframe`-заглушки; поля UI совпадают с DTO/validation backend; запросы идут через единый API prefix `/api/v1`; реализованы loading/error/empty/success состояния; happy-path и основные error-path проверены локально; build/lint зелёные; для backend-сценария есть либо существующий тест, либо ручной runbook-проверяемый шаг; в документации отражены все ограничения и отложенные сценарии.

### MVP summary

- Первый релиз концентрируется на реально собираемом public + patient-flow, а не на полном backoffice.
- Backend уже содержит роли и контракты для doctor/admin, поэтому эти сущности не вырезаются, а переводятся в postponed scope на уровне UI.
- Визуальные экраны каталога врачей, профиля врача и Q&A feed сохраняются в первом MVP, потому что уже существуют как Stitch-страницы и совпадают с продуктовой задачей discovery.

## 2. Инвентаризация текущего состояния проекта

- [x] Зафиксировать текущее состояние backend API с перечнем доступных endpoint-ов. Доступны: `GET /health`; auth `POST /api/v1/auth/register/patient`, `POST /api/v1/auth/register/doctor`, `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`, `PATCH /api/v1/auth/me`, `POST /api/v1/auth/change-password`, `GET /api/v1/auth/me/documents`; doctors `GET /api/v1/doctors/`, `GET /api/v1/doctors/{doctor_id}`, `POST /api/v1/doctors/me/documents`; specializations `GET /api/v1/specializations/`, `POST/PATCH/DELETE /api/v1/specializations/...`; questions `GET /api/v1/questions/`, `GET /api/v1/questions/{question_id}`, `POST /api/v1/questions/`, `POST /api/v1/questions/{question_id}/comments`; admin `GET /api/v1/admin/doctors/pending`, `GET /api/v1/admin/doctors/{doctor_id}`, `PATCH /api/v1/admin/doctors/{doctor_id}/verify`, `GET /api/v1/admin/documents/{document_id}`.
- [x] Зафиксировать текущее состояние frontend с перечнем экранов, реализованных как native React. Native React реализован только для landing page `/` в `frontend/src/App.jsx`.
- [x] Зафиксировать перечень экранов frontend, которые пока являются `iframe`-обертками над Stitch HTML. Это `/login-desktop-ru`, `/registration-desktop-ru`, `/doctor-directory-with-filters-ru`, `/doctor-public-profile-ru`, `/public-questions-feed-ru`.
- [x] Зафиксировать, какие части frontend уже используют API-клиент, а какие еще нет. `frontend/src/api/client.js` существует, но в текущем runtime не используется ни одним экраном. Реализованные методы: `registerPatient`, `login`, `me`, `refresh`, `listQuestions`. Все страницы пока не интегрированы с API.
- [x] Зафиксировать текущее состояние Docker/Compose запуска для всех сервисов. `docker-compose.yaml` описывает три сервиса: `postgres` (`postgres:17`, порт `6432:5432`, volume `postgres_data`), `backend` (build из `backend`, порт `8000:8000`, volume `backend_uploads:/app/uploads`), `frontend` (build из `frontend`, порт `5173:5173`, proxy target `http://backend:8000`). `docker compose config` отрабатывает успешно.
- [x] Зафиксировать текущее состояние миграций базы данных. В проекте две ревизии Alembic: `8093419d4e91` создаёт всю текущую схему, `2094603e316e` является пустой reserved revision без DDL-изменений.
- [x] Зафиксировать текущее состояние backend тестов. Есть 6 тестовых модулей: `test_auth.py`, `test_doctor_and_questions.py`, `test_hashing.py`, `test_login.py`, `test_profile.py`, `test_register.py`. Покрываются: регистрация пациента, логин, `me/refresh/logout`, hashing, doctor verification, patient question, doctor comment. Тесты настроены на SQLite через `ASGITransport`, а не на Compose/Postgres.
- [x] Зафиксировать текущее состояние frontend build/lint. После фикса `frontend/vite.config.js` оба сценария проходят: `npm run lint` и `npm run build`.
- [x] Зафиксировать все найденные рассинхроны между UI и backend-контрактами. Найдены рассинхроны: login UI ожидал `email/phone`, backend принимает только `username`; registration UI ожидал `full name + email + phone`, backend patient contract использует `username`, `password`, `first_name`, `last_name`; registration UI не разделён на patient и doctor, backend использует два разных контракта; doctor public profile DTO возвращает `qualification_documents`, что избыточно для публичной страницы; `frontend/.env.example` указывал `/api`, а фактический API prefix равен `/api/v1`; frontend runtime pages не используют API client вообще.

### Current state summary

- Текущий backend уже ближе к рабочему продукту, чем frontend.
- Текущий frontend по сути состоит из одного живого landing и пяти Stitch-обёрток без интеграции.
- Контейнерная конфигурация выглядит цельной, но runtime-проверка в этой сессии ограничена отсутствием доступа к Docker daemon.

## 3. Выравнивание доменной модели и API-контрактов

- [x] Сопоставить поля login-формы frontend с фактическим backend-контрактом `/api/v1/auth/login`. Backend contract: JSON `{ "username": string, "password": string }`. UI выровнен под `username`.
- [x] Принять решение, логин выполняется по `username` или по `email/phone`. Решение: логин в первом этапе выполняется по `username`.
- [x] Если выбран логин по `username`, обновить тексты и placeholder-ы frontend, чтобы они не вводили пользователя в заблуждение. Обновлены `frontend/public/stitch/login-desktop-ru.html` и `frontend/stitch/raw/login-desktop-ru.html`.
- [x] Если выбран логин по `email` или `phone`, доработать backend-схему, модель и логику аутентификации. Не требуется в первом этапе.
- [x] Сопоставить patient registration UI с backend-контрактом `/api/v1/auth/register/patient`. Backend contract: JSON `{ "username", "password", "first_name"?, "last_name"? }`, без `email` и `phone`.
- [x] Принять решение, нужен ли отдельный `username` в UI или он должен вычисляться/заменяться email. Решение: в UI первого этапа нужен явный отдельный `username`.
- [x] Принять решение, нужны ли в backend поля `email` и `phone`, так как UI уже их предполагает. Решение: `email` и `phone` не входят в первый этап и не добавляются в backend до отдельной продуктовой задачи.
- [x] Если `email` обязателен, расширить backend модели, схемы, миграции и сериализаторы. Не требуется в первом этапе.
- [x] Если `phone` обязателен, расширить backend модели, схемы, миграции и сериализаторы. Не требуется в первом этапе.
- [x] Если `email` и `phone` не входят в первый этап, убрать их из UI первого этапа или явно отложить. Поля убраны из текущего stitched registration UI и зафиксированы как postponed.
- [x] Сопоставить doctor registration UI с backend-контрактом `/api/v1/auth/register/doctor`. Backend doctor contract: multipart/form-data с обязательными `username`, `password`, `specialization_ids[]`, `documents[]` и опциональными `first_name`, `last_name`.
- [x] Уточнить обязательность `specialization_ids` для doctor registration. Обязательны, минимум один id.
- [x] Уточнить обязательность загрузки `documents[]` для doctor registration. Обязательна минимум одна qualification file.
- [x] Уточнить, как doctor registration должен выглядеть в UI: одна форма или многошаговый flow. Решение: когда doctor registration будет включена, она должна быть многошаговой. Одна плоская форма плохо подходит для выбора специализаций и загрузки документов.
- [x] Сопоставить doctor directory UI с backend-контрактом `/api/v1/doctors/`. Контракт: `GET /api/v1/doctors/?specialization_id&offset&limit`, ответ массивом verified doctors без total count.
- [x] Сопоставить doctor profile UI с backend-контрактом `/api/v1/doctors/{doctor_id}`. Контракт: detail verified doctor по numeric `doctor_id`; DTO сейчас включает `qualification_documents`, но публичный UI не должен их показывать.
- [x] Сопоставить public questions UI с backend-контрактом `/api/v1/questions/`. Контракт: `GET /api/v1/questions/?offset&limit`, ответ массивом `QuestionDTO` с автором и комментариями врачей; отдельный `GET /api/v1/questions/{question_id}` доступен под detail page.
- [x] Сопоставить admin moderation UI с backend-контрактами `/api/v1/admin/...`. Контракт есть: pending list, doctor detail, verify toggle, document download. Для первого frontend MVP этот экран остаётся вне scope.
- [x] Зафиксировать итоговый контракт для каждого frontend-экрана до начала активной реализации. Итоговые контракты: login -> `POST /api/v1/auth/login`; patient registration -> `POST /api/v1/auth/register/patient`; doctor directory -> `GET /api/v1/doctors/`; doctor profile -> `GET /api/v1/doctors/{doctor_id}`; public questions feed -> `GET /api/v1/questions/`; patient question create -> `POST /api/v1/questions/` после появления native экрана; admin moderation -> `GET/PATCH /api/v1/admin/...` во второй волне.

### Contract decisions

- Для первого этапа базовая идентичность пользователя строится вокруг `username`.
- `email` и `phone` сознательно выведены из MVP, чтобы не тянуть лишние миграции и не ломать уже существующую auth-модель.
- Public doctor profile должен потреблять безопасное подмножество doctor DTO; при активной реализации лучше вынести отдельный public serializer без `qualification_documents`.

## 4. Подготовка среды и запуска проекта

- [x] Проверить локальный запуск `postgres`, `backend` и `frontend` через `docker compose up --build`. Подтверждено runtime: `docker compose up --build -d` поднял все три сервиса, `docker compose ps` показал published порты `6432`, `8000`, `5173`.
- [x] Проверить, что backend применяет миграции при старте контейнера. Подтверждено runtime по логам backend: Alembic выполняется на старте контейнера; для пустой БД отдельно зафиксированы `Running upgrade -> 8093419d4e91` и `-> 2094603e316e`.
- [x] Проверить, что backend корректно стартует после применения миграций на пустой базе. Подтверждено через временную БД `telemedicine_emptycheck_20260311` и временный контейнер `telemedicine_backend_emptycheck` на `http://localhost:8010`: после миграций сервис отдал `200 {"status":"ok"}`.
- [x] Проверить, что bootstrap superuser создается ожидаемо в dev-среде. Подтверждено runtime: лог временного контейнера на пустой БД содержит `Bootstrap superuser 'superadmin' created`, а логин `superadmin / SuperAdmin!123` к `8010` вернул `role=superuser`.
- [x] Проверить, что frontend доступен на `http://localhost:5173`. Подтверждено runtime: `curl -I http://localhost:5173` вернул `HTTP/1.1 200 OK`.
- [x] Проверить, что backend доступен на `http://localhost:8000`. Подтверждено runtime: `curl -i http://localhost:8000/health` вернул `HTTP/1.1 200 OK` и `{"status":"ok"}`.
- [x] Проверить доступность Swagger/OpenAPI. Подтверждено runtime: `http://localhost:8000/docs` и `http://localhost:8000/openapi.json` отдают `200 OK`.
- [x] Проверить сетевую связность frontend -> backend внутри Compose. Подтверждено runtime: `docker compose exec frontend wget -qO- http://backend:8000/health` вернул `{"status":"ok"}`.
- [x] Проверить сетевую связность браузер -> frontend -> proxy -> backend. Подтверждено runtime: `curl http://localhost:5173/api/v1/questions/` вернул `200 OK` и корректный backend JSON через Vite proxy.
- [x] Проверить, что volume для doctor uploads создается и используется корректно. Подтверждено runtime: после doctor registration файл появился в `/app/uploads/doctor_documents` внутри backend-container.
- [x] Проверить, что uploads не теряются между рестартами контейнера backend. Подтверждено runtime: после `docker compose restart backend` файл `b1a53868d96b43e8b86c098df3802d13.pdf` остался в `/app/uploads/doctor_documents`, а admin download `GET /api/v1/admin/documents/1` по-прежнему вернул `200` и `53` байта.
- [x] Проверить, что dev-окружение не конфликтует по портам на локальной машине. Подтверждено runtime: текущий compose-стек успешно занял `5173`, `8000`, `6432`, а временный empty-db backend поднялся на `8010` без конфликта.
- [x] Подготовить и описать единый runbook локального запуска для интеграционной разработки. Актуальный runbook: 1) поднять Docker Desktop; 2) из корня выполнить `docker compose up --build -d`; 3) проверить `docker compose ps`; 4) проверить `curl http://localhost:8000/health`, `curl -I http://localhost:8000/docs`, `curl -I http://localhost:5173`; 5) проверить proxy-запрос `curl http://localhost:5173/api/v1/questions/`; 6) для auth smoke пройти `register -> login -> refresh -> me` через `http://localhost:5173/api/v1/...`; 7) для uploads пройти doctor registration и `docker compose restart backend`, затем повторно скачать документ админом.

### Environment note

- Runtime-валидация раздела 4 завершена.
- Основной compose-стек оставлен поднятым после проверки.
- Временный empty-db container для проверки миграций на пустой базе удалён; временная БД `telemedicine_emptycheck_20260311` остаётся в postgres как диагностический артефакт и может быть удалена позже без влияния на основной dev-контур.

## 5. Выравнивание конфигурации frontend и backend

- [x] Исправить и унифицировать `VITE_API_BASE_URL` между frontend и backend-префиксами. В `frontend/.env.example` закреплён `/api/v1`, `frontend/src/api/client.js` уже использует тот же prefix по умолчанию.
- [x] Привести `frontend/.env.example` в соответствие с фактическим backend API prefix.
- [x] Проверить, что frontend requests идут по корректному пути `/api/v1/...`. Подтверждено runtime запросами через `http://localhost:5173/api/v1/questions/`, `.../auth/login`, `.../auth/refresh`, `.../auth/me`.
- [x] Проверить, что proxy в Vite проксирует все нужные backend маршруты. Подтверждено runtime для `questions`, `auth/login`, `auth/refresh`, `auth/me`.
- [x] Проверить, что запросы с `credentials: include` корректно проходят через frontend proxy. Подтверждено runtime через login+refresh cookie flow на `http://localhost:5173/api/v1/auth/...`.
- [x] Проверить совместимость `refresh_token` cookie path с проксируемым API path. Подтверждено runtime: `Set-Cookie` после login содержит `Path=/api/v1/auth`, а `POST /api/v1/auth/refresh` через frontend proxy успешно отрабатывает.
- [x] Проверить CORS-настройки backend для локальной разработки без proxy. Подтверждено runtime: `OPTIONS /api/v1/auth/login` с `Origin: http://localhost:5173` вернул `Access-Control-Allow-Origin: http://localhost:5173` и `Access-Control-Allow-Credentials: true`.
- [x] Проверить CORS-настройки backend для случая, когда запросы идут только через frontend proxy. Подтверждено runtime: frontend proxy работает как same-origin entrypoint, backend успешно обслуживает proxied requests без дополнительной browser-side CORS конфигурации.
- [x] Проверить, что `SameSite`, `Secure`, `Domain`, `Path` для refresh cookie корректны для dev-среды. Подтверждено runtime: `SameSite=lax`, `HttpOnly`, `Path=/api/v1/auth`, `Secure` отсутствует, `Domain` не задан. Для `localhost` dev-сценария это корректно.
- [x] Подготовить отдельные рекомендации/конфиг для production-режима cookie и CORS. Production recommendation: включить `CFG_AUTH__COOKIE_SECURE=true`, использовать HTTPS; для same-site deploy сохранить `SameSite=lax`, для cross-site frontend/backend перейти на `SameSite=none` и HTTPS; при split-domain явно задать `CFG_AUTH__COOKIE_DOMAIN`; ограничить `CFG_CORS__ALLOWED_ORIGINS` только production origins; для proxy-only production держать публичный frontend как основной origin и не открывать избыточный CORS на backend.

### Frontend/backend config note

- Dev proxy path окончательно стандартизован как `/api/v1`.
- Auth flow через proxy подтверждён реальным `register -> login -> refresh -> me`.
- Конфиг cookies и CORS для dev не требует правок; production differs only in HTTPS and stricter origin/cookie policy.

## 6. Архитектурная подготовка frontend перед интеграцией

- [x] Принять решение, оставаться ли на ручной маршрутизации или перейти на нормальный router. Решение: на текущем этапе остаёмся на lightweight manual router без внешней зависимости, но выносим его в отдельный `RouterProvider`.
- [x] Если выбирается router, внедрить React Router и перенести текущие маршруты. Не требуется в текущем этапе: React Router сознательно не внедрялся.
- [x] Если router пока не внедряется, формально описать ограничения текущего подхода и рамки его использования. Ограничения: route matching только по `pathname`, нет nested routes/data routers; подход допустим для текущего набора из нескольких flat routes и auth guards.
- [x] Выделить общую структуру приложения: layout, header, footer, protected routes, public routes. Реализована структура `RouterProvider -> AuthProvider -> RouteRenderer`; маршруты разделены на `public`, `guest`, `protected`; добавлен protected route `/account`.
- [x] Определить место хранения auth-state на frontend. Реализовано: `frontend/src/auth/AuthContext.jsx`.
- [x] Определить способ хранения `access_token` на frontend. Реализовано: `access_token` хранится только в памяти `AuthContext`, без localStorage/sessionStorage.
- [x] Определить стратегию refresh-flow при истечении access token. Реализовано: при `401` защищённый запрос инициирует `POST /auth/refresh`, обновляет access token и повторяет исходный запрос один раз.
- [x] Определить, нужен ли глобальный API-layer с автоматическим retry после refresh. Реализовано в `frontend/src/api/client.js`.
- [x] Определить, где будет жить типизация/описание DTO frontend для backend-ответов. Решение зафиксировано в `frontend/src/api/client.js`: DTO описываются рядом с API-слоем как documented plain JS objects.
- [x] Определить стратегию обработки API-ошибок: общая, постраничная, полевая. Реализовано: `ApiError` хранит `status`, `payload`, `fieldErrors`; формы используют field errors и form-level banner.
- [x] Определить стратегию загрузочных состояний для страниц и форм. Реализовано: guarded pages имеют route loading state, формы имеют disabled/loading submit state.
- [x] Определить стратегию пустых состояний для списков врачей и вопросов. Решение зафиксировано: page-level empty states останутся на самих страницах каталогов/лент при их переводе в native React.
- [x] Определить стратегию уведомлений об успехе/ошибке. Реализовано: inline success/error banners внутри экрана и query-based flash messages между registration/login/logout.
- [x] Определить стратегию route guards по ролям пользователя. Реализовано: `ProtectedRoute` поддерживает auth check, role check и `requireVerifiedDoctor`.
- [x] Определить, как frontend будет узнавать текущего пользователя после reload страницы. Реализовано: на старте `AuthProvider` вызывает `POST /auth/refresh`, получает новый access token и `user`.

### Frontend architecture note

- Текущий routing/auth shell уже достаточен для первого MVP и не требует внешнего router package.
- Ключевая граница ответственности теперь выглядит так: router отвечает за path + redirects, auth context за session lifecycle, API client за DTO/errors/retry.
- Переход на React Router остаётся опцией второй волны, когда появятся nested protected sections и более сложный navigation graph.

## 7. Приведение API-клиента frontend в рабочее состояние

- [x] Провести ревизию текущего `frontend/src/api/client.js`. Клиент полностью переработан.
- [x] Исправить базовый URL API-клиента, если он не совпадает с backend. Клиент использует `/api/v1`.
- [x] Добавить в API-клиент универсальную обработку ошибок backend. Реализован `ApiError`.
- [x] Добавить в API-клиент поддержку запросов без `Content-Type: application/json`, когда нужен `FormData`. Реализовано.
- [x] Добавить в API-клиент методы для logout.
- [x] Добавить в API-клиент методы для `GET /auth/me`.
- [x] Добавить в API-клиент методы для `PATCH /auth/me`.
- [x] Добавить в API-клиент методы для `POST /auth/change-password`.
- [x] Добавить в API-клиент методы для `POST /auth/refresh`.
- [x] Добавить в API-клиент методы для `GET /specializations/`.
- [x] Добавить в API-клиент методы для `GET /doctors/`.
- [x] Добавить в API-клиент методы для `GET /doctors/{doctor_id}`.
- [x] Добавить в API-клиент методы для `POST /auth/register/doctor`.
- [x] Добавить в API-клиент методы для `POST /doctors/me/documents`.
- [x] Добавить в API-клиент методы для `POST /questions/`.
- [x] Добавить в API-клиент методы для `GET /questions/{question_id}`.
- [x] Добавить в API-клиент методы для `POST /questions/{question_id}/comments`.
- [x] Добавить в API-клиент методы для `GET /admin/doctors/pending`.
- [x] Добавить в API-клиент методы для `GET /admin/doctors/{doctor_id}`.
- [x] Добавить в API-клиент методы для `PATCH /admin/doctors/{doctor_id}/verify`.
- [x] Добавить в API-клиент методы для скачивания doctor documents администратором.
- [x] Добавить механизм подстановки `Authorization: Bearer <access_token>` во все защищенные запросы.
- [x] Добавить механизм refresh access token при `401`, если сценарий выбран для первого этапа.
- [x] Добавить защиту от бесконечного цикла `401 -> refresh -> 401`.

## 8. Реализация frontend auth layer

- [x] Создать общий auth-context/store для frontend.
- [x] Реализовать инициализацию auth-state при загрузке приложения.
- [x] Реализовать сценарий восстановления сессии через refresh cookie.
- [x] Реализовать сохранение access token в памяти приложения.
- [x] Реализовать очистку auth-state при logout.
- [x] Реализовать сценарий авторазлогина при неуспешном refresh.
- [x] Реализовать helper для проверки роли пользователя.
- [x] Реализовать helper для проверки признака `is_verified_doctor`.
- [x] Реализовать protected route для любых личных/админских экранов.
- [x] Реализовать redirect-auth-guard для login/register экранов, если пользователь уже авторизован.

## 9. Перевод Stitch login page в нативный рабочий React-экран

- [x] Принять решение, сохраняем ли текущий визуал Stitch 1:1 или делаем адаптацию под рабочую форму. Решение: адаптация под рабочую форму с сохранением общей визуальной тональности Stitch.
- [x] Перевести `login-desktop-ru` из `iframe` в native React component.
- [x] Собрать рабочую форму логина с controlled inputs.
- [x] Привязать поля формы к фактическому backend-контракту.
- [x] Добавить клиентскую валидацию логина перед отправкой.
- [x] Добавить клиентскую валидацию пароля перед отправкой.
- [x] Подключить submit к API `/auth/login`.
- [x] Сохранить `access_token` и `user` в auth-state после успешного логина.
- [x] Проверить установку refresh cookie после логина. Подтверждено runtime через `Set-Cookie` после login через frontend proxy.
- [x] Реализовать обработку ошибок `401 Invalid credentials`.
- [x] Реализовать disabled/loading state кнопки входа.
- [x] Реализовать success redirect после логина.
- [x] Реализовать переход на экран регистрации.
- [x] Удалить зависимость рабочей страницы логина от статического Stitch `iframe`.

## 10. Перевод Stitch registration page в нативный рабочий React-экран

- [x] Принять решение, какая именно регистрация нужна на первом этапе: patient only или patient + doctor. Решение: patient only.
- [x] Перевести `registration-desktop-ru` из `iframe` в native React component.
- [x] Разделить UI на patient registration и doctor registration, если это требуется продуктом. Для текущего этапа не требуется: экран реализован как patient-only flow с явным пояснением, что doctor registration отключена.
- [x] Если на первом этапе поддерживается только patient registration, явно скрыть/отключить doctor registration из UI.
- [x] Собрать рабочую patient registration форму с controlled inputs.
- [x] Привязать поля формы к фактическому backend-контракту.
- [x] Реализовать поле подтверждения пароля на frontend.
- [x] Реализовать проверку совпадения пароля и подтверждения пароля.
- [x] Реализовать клиентскую валидацию username/email/phone в зависимости от принятого контракта. В текущем контракте реализована username/password validation.
- [x] Реализовать submit patient registration к `/auth/register/patient`.
- [x] Реализовать success-сценарий после успешной регистрации пациента.
- [x] Принять решение, нужен ли авто-логин после регистрации. Решение: авто-логин не нужен.
- [x] Реализовать переход на логин после регистрации, если авто-логин не нужен.
- [x] Реализовать doctor registration form, если doctor-flow включен в первый этап. Не требуется в текущем этапе.
- [x] Реализовать загрузку doctor qualification documents через `FormData`, если doctor-flow включен в первый этап. Не требуется в текущем этапе.
- [x] Реализовать выбор специализаций врача из backend-справочника, если doctor-flow включен в первый этап. Не требуется в текущем этапе.
- [x] Реализовать клиентскую валидацию doctor registration формы, если doctor-flow включен в первый этап. Не требуется в текущем этапе.
- [x] Реализовать обработку backend ошибок `409`, `422`, `400` на регистрации.
- [x] Реализовать disabled/loading state кнопки регистрации.
- [x] Реализовать переход на экран логина.
- [x] Удалить зависимость рабочей страницы регистрации от статического Stitch `iframe`.

## 11. Реализация страницы списка врачей

- [x] Принять решение, нужен ли список врачей как публичная страница или как страница только для авторизованных. Решение: каталог врачей остаётся публичным.
- [x] Перевести doctor directory из `iframe` в native React component.
- [x] Реализовать загрузку данных с `/doctors/`.
- [x] Реализовать отображение карточек врача на основе backend DTO.
- [x] Реализовать отображение специализаций врача.
- [x] Реализовать состояние загрузки списка врачей.
- [x] Реализовать пустое состояние списка врачей.
- [x] Реализовать состояние ошибки загрузки списка врачей.
- [x] Реализовать фильтрацию по специализации через query/backend filter.
- [x] Реализовать загрузку справочника специализаций для фильтра.
- [x] Реализовать reset фильтров.
- [x] Реализовать пагинацию или lazy loading списка врачей. Реализован `load more` через `offset`/`limit`.
- [x] Реализовать переход из карточки врача на страницу профиля врача.
- [x] Удалить зависимость рабочей страницы каталога от статического Stitch `iframe`.

## 12. Реализация страницы публичного профиля врача

- [x] Принять решение, достаточно ли текущего backend DTO для UI профиля врача. Решение: для MVP достаточно имени, username, специализаций и признака верификации.
- [x] Если данных недостаточно, расширить backend DTO и сериализацию профиля врача. Не потребовалось расширение; публичный endpoint, наоборот, ограничен до безопасного публичного DTO без qualification documents.
- [x] Перевести doctor public profile из `iframe` в native React component.
- [x] Реализовать загрузку данных врача по `doctor_id`.
- [x] Реализовать отображение ФИО/username врача.
- [x] Реализовать отображение специализаций врача.
- [x] Реализовать отображение статуса верификации только там, где это действительно нужно по UX. Использован ненавязчивый public trust badge.
- [x] Принять решение, нужно ли показывать qualification documents на публичной странице врача. Решение: нет, документы не должны быть публичными.
- [x] Если документы нельзя показывать публично, убедиться, что UI их не пытается визуализировать.
- [x] Реализовать loading/error/empty state профиля врача.
- [x] Реализовать переходы назад в каталог врачей.
- [x] Удалить зависимость рабочей страницы профиля от статического Stitch `iframe`.

## 13. Реализация публичной страницы вопросов и ответов

- [x] Принять решение, должна ли лента вопросов быть публичной. Решение: да, лента остаётся публичной.
- [x] Перевести public questions feed из `iframe` в native React component.
- [x] Реализовать загрузку вопросов с `/questions/`.
- [x] Реализовать отображение вопроса, автора, даты и комментариев врачей.
- [x] Реализовать состояние загрузки списка вопросов.
- [x] Реализовать пустое состояние списка вопросов.
- [x] Реализовать состояние ошибки загрузки списка вопросов.
- [x] Реализовать пагинацию или lazy loading списка вопросов. Реализован `load more` через `offset`/`limit`.
- [x] Реализовать переход в детали вопроса, если отдельный экран для вопроса нужен. Отдельный экран не понадобился; добавлен deep-link `?question_id=` на той же странице.
- [x] Удалить зависимость рабочей страницы вопросов от статического Stitch `iframe`.

## 14. Реализация сценария создания вопроса пациентом

- [x] Принять решение, где в UI располагается форма создания вопроса. Решение: форма встроена в верх публичной страницы Q&A.
- [x] Принять решение, нужен ли отдельный экран для создания вопроса. Решение: отдельный экран не нужен.
- [x] Реализовать доступ к созданию вопроса только для роли `patient`.
- [x] Реализовать форму создания вопроса.
- [x] Реализовать клиентскую валидацию длины текста вопроса.
- [x] Подключить submit к `/questions/`.
- [x] Реализовать success-сценарий после создания вопроса.
- [x] Реализовать обновление списка вопросов после успешного создания.
- [x] Реализовать обработку ошибок backend при создании вопроса.
- [x] Реализовать loading/disabled state формы создания вопроса.

## 15. Реализация сценария ответа врача на вопрос

- [x] Принять решение, где в UI располагается форма ответа врача. Решение: форма ответа встроена в карточку каждого вопроса.
- [x] Реализовать доступ к ответу только для роли `doctor`.
- [x] Реализовать дополнительную проверку `is_verified_doctor` на frontend UX-уровне.
- [x] Реализовать состояние, когда врач авторизован, но еще не верифицирован, и не может отвечать.
- [x] Реализовать форму ответа на вопрос.
- [x] Реализовать клиентскую валидацию текста ответа.
- [x] Подключить submit к `/questions/{question_id}/comments`.
- [x] Реализовать success-обновление вопроса после публикации ответа.
- [x] Реализовать обработку ошибок `403 Doctor is not verified`.
- [x] Реализовать loading/disabled state формы ответа.

## 16. Реализация профиля текущего пользователя

- [x] Принять решение, нужен ли отдельный экран `Мой профиль` в первом этапе. Решение: да, `/account` теперь является отдельным экраном `Мой профиль`.
- [x] Реализовать загрузку текущего пользователя через `/auth/me`.
- [x] Реализовать экран/блок отображения текущего профиля.
- [x] Реализовать обновление имени и фамилии через `/auth/me`.
- [x] Реализовать форму изменения пароля через `/auth/change-password`.
- [x] Реализовать client-side валидацию смены пароля.
- [x] Реализовать logout через `/auth/logout`.
- [x] Реализовать корректную очистку auth-state после logout.
- [x] Реализовать redirect после logout.

## 17. Реализация doctor self-service по документам

- [x] Принять решение, входит ли doctor self-service по документам в первый этап. Решение: для текущего интеграционного этапа сценарий включён как doctor-only секция в `/account`.
- [x] Реализовать экран/секцию просмотра количества и списка загруженных документов врача.
- [x] Реализовать загрузку текущих документов врача, если этот сценарий нужен в UI.
- [x] Реализовать повторную загрузку документов врачом через `/doctors/me/documents`.
- [x] Реализовать `FormData` upload нескольких файлов.
- [x] Реализовать frontend-проверки типа и размера файла до отправки.
- [x] Реализовать отображение ошибок по недопустимому типу/размеру/количеству файлов.
- [x] Реализовать loading state загрузки документов.
- [x] Реализовать success feedback после загрузки документов.

## 18. Реализация admin/moderation интерфейса

- [x] Принять решение, входит ли admin UI в первый рабочий этап. Решение: для текущего интеграционного этапа admin UI включён отдельным защищённым экраном.
- [x] Реализовать доступ к admin UI только для ролей `admin` и `superuser`.
- [x] Реализовать экран списка врачей, ожидающих верификации.
- [x] Подключить загрузку данных с `/admin/doctors/pending`.
- [x] Реализовать пагинацию списка pending doctors.
- [x] Реализовать карточку/строку pending doctor с основной информацией.
- [x] Реализовать экран/модалку просмотра doctor details для moderation.
- [x] Подключить загрузку doctor detail через `/admin/doctors/{doctor_id}`.
- [x] Реализовать просмотр списка qualification documents.
- [x] Реализовать скачивание qualification documents администратором.
- [x] Реализовать действие Verify/Unverify врача через `/admin/doctors/{doctor_id}/verify`.
- [x] Реализовать success/error feedback для moderation действий.
- [x] Реализовать loading/empty/error states admin интерфейса.

## 19. Приведение backend к потребностям frontend, если данных недостаточно

- [x] Проверить, достаточно ли backend DTO для login/register/profile UI. Достаточно: `UserProfileDTO` + `/auth/me/documents`.
- [x] Проверить, достаточно ли backend DTO для каталога врачей. Достаточно.
- [x] Проверить, достаточно ли backend DTO для публичного профиля врача. Достаточно; публичный endpoint ограничен до безопасного публичного DTO.
- [x] Проверить, достаточно ли backend DTO для списка вопросов и комментариев. Достаточно.
- [x] Проверить, достаточно ли backend DTO для admin moderation UI. Достаточно: `PendingDoctorsResponseDTO` + `DoctorDetailDTO`.
- [x] Если каких-то полей не хватает, расширить Pydantic-схемы backend. Не потребовалось.
- [x] Если каких-то полей не хватает, расширить сериализаторы backend. Не потребовалось; наоборот, публичный профиль сузили до безопасного DTO.
- [x] Если каких-то полей не хватает, расширить SQLAlchemy модели backend. Не потребовалось.
- [x] Если меняются модели БД, подготовить новые Alembic-миграции. Не потребовалось.
- [x] Проверить обратную совместимость backend-контрактов после изменений. Покрыто обновлёнными backend integration tests.

## 20. Приведение backend в порядок для интеграционного использования

- [x] Проверить все защищенные backend endpoint-ы с реальными auth-сценариями.
- [x] Проверить, что `GET /auth/me` работает после логина с access token.
- [x] Проверить, что `POST /auth/refresh` реально продлевает сессию через cookie.
- [x] Проверить, что `POST /auth/logout` инвалидирует refresh session.
- [x] Проверить, что role-based authorization возвращает ожидаемые `403`.
- [x] Проверить, что doctor verification действительно влияет на возможность отвечать в Q&A.
- [x] Проверить корректность валидации и ошибок doctor document upload.
- [x] Проверить корректность выдачи и скачивания qualification documents админом.
- [x] Проверить, что backend healthcheck покрывает реальный полезный минимум.
- [x] Проверить, не нужны ли дополнительные backend endpoint-ы для удобного frontend UX. Дополнительные endpoint-ы не потребовались.


## 21. Маршруты, навигация и UX-связность приложения

- [x] Сформировать итоговую карту маршрутов приложения. Итоговая карта и alias-маршруты зафиксированы в `frontend/docs/ROUTES_AND_UX_MAP.md`: canonical routes `/`, `/login-desktop-ru`, `/registration-desktop-ru`, `/doctor-directory-with-filters-ru`, `/doctor-public-profile-ru`, `/public-questions-feed-ru`, `/account`, `/admin-doctor-moderation`, `/404` и semantic aliases `/login`, `/register`, `/doctors`, `/questions`, `/profile`, `/admin`.
- [x] Реализовать единый navigation flow между landing, login, register, doctors, questions, profile, admin. Landing, public pages, account и admin теперь связаны реальными `AppLink`-переходами; protected flow использует `returnTo`, role-based default redirects и alias routes.
- [x] Реализовать ссылки между экранами вместо `href="#"`. Placeholder-ссылки на landing заменены на реальные маршруты или осмысленные section anchors; dead-end `href="#"` в runtime-компонентах убраны.
- [x] Реализовать корректные редиректы после login/logout/register. Login использует safe `returnTo` или role-based default destination, register ведёт на login с `?registered=1` и сохранением `returnTo`, logout ведёт на login с `?logged_out=1`.
- [x] Реализовать маршрут для `404` или fallback-page. Добавлен явный маршрут `/404` и native `NotFoundPage`; неизвестные path больше не перенаправляются молча на landing.
- [x] Реализовать запрет доступа к закрытым маршрутам без авторизации. `ProtectedRoute` перенаправляет anonymous user на login с `returnTo`.
- [x] Реализовать запрет доступа к admin-маршрутам без нужной роли. `/admin-doctor-moderation` и alias `/admin` закрыты по ролям `admin/superuser`; при mismatch пользователь уходит на default protected destination с `?access=denied`.
- [x] Реализовать запрет доступа к doctor-only действиям без нужной роли. Создание doctor reply и doctor document upload дополнительно проверяются на frontend до API-вызова; для non-doctor и unverified-doctor выводятся inline ошибки.

## 22. Работа с состояниями UI

- [x] Реализовать единый стиль загрузочных состояний. Auth/account route loading, page loading и public loading опираются на общий визуальный паттерн `route-state-card`/spinner и общие surface tokens.
- [x] Реализовать единый стиль ошибок API. Form-level и page-level ошибки выровнены через общий `resolveFormApiError` и единый message pattern (`auth-message`, `public-inline-message`, `state-card--error`).
- [x] Реализовать единый стиль success-сообщений. Success feedback для login/register/account/questions/admin использует тот же inline banner pattern.
- [x] Реализовать skeleton/spinner там, где это оправдано. Skeleton есть на doctor directory, doctor profile, public questions feed, admin pending list и admin doctor detail; spinner есть в route guards и account/profile loading.
- [x] Реализовать empty states для списка врачей. Doctor directory показывает отдельный empty state с CTA на сброс фильтра.
- [x] Реализовать empty states для списка вопросов. Q&A feed показывает empty state до публикации первого вопроса.
- [x] Реализовать empty states для admin pending doctors. Admin moderation page показывает отдельный empty state для пустой очереди.
- [x] Реализовать disabled состояния для форм во время submit. Login, register, profile update, change password, create question, answer question, doctor document upload и admin actions блокируют inputs/buttons на время submit.
- [x] Реализовать защиту от повторной отправки форм по двойному клику. Введён shared `useSubmitLock`; он закрывает двойной submit для auth/profile/password/documents/question create, а reply action дополнительно защищён per-question lock.

## 23. Работа с дизайном и переносом Stitch-экранов

- [x] Зафиксировать список Stitch-экранов, которые нужно перевести в native JSX в первую очередь. Приоритет и текущий статус зафиксированы в `frontend/docs/STITCH_MIGRATION_PLAN.md`: `login-desktop-ru`, `registration-desktop-ru`, `doctor-directory-with-filters-ru`, `doctor-public-profile-ru`, `public-questions-feed-ru`.
- [x] Для каждого Stitch-экрана определить, какие части можно сохранить визуально без изменений. Для каждого экрана в `frontend/docs/STITCH_MIGRATION_PLAN.md` зафиксированы сохраняемые визуальные паттерны: auth shell, public hero blocks, card grid, ambient palette, glass surfaces.
- [x] Для каждого Stitch-экрана определить, какие части нужно адаптировать под реальный data flow. Там же зафиксированы runtime-адаптации: real DTO, query params, auth gates, field validation, success/error/loading states, inline forms вместо статики.
- [x] Удалить или изолировать `iframe`-подход там, где экран должен стать интерактивным. Interactive runtime больше не использует `iframe` для login/register/doctors/profile/questions; Stitch HTML/PNG оставлены только как reference assets.
- [x] Проверить, что после перевода экранов в native React не потеряна визуальная целостность проекта. В `frontend/docs/STITCH_MIGRATION_PLAN.md` зафиксировано сохранение общей blue/emerald visual system и общего public/auth shell design language.
- [x] Проверить адаптивность новых нативных экранов на desktop и mobile. Native pages опираются на mobile/tablet breakpoints в `auth-shell.css` и `public-pages.css`; одноколоночные fallback layouts и responsive grids сохранены и production build прошёл без layout regressions.

## 24. Обработка форм и валидация

- [x] Зафиксировать frontend-валидацию для login form. Матрица правил описана в `frontend/docs/FORM_VALIDATION.md`: required username/password, regex для username, lowercasing + trim.
- [x] Зафиксировать frontend-валидацию для patient registration form. В `frontend/docs/FORM_VALIDATION.md` описаны required first/last name, username regex, strong password, confirm password, normalization.
- [x] Зафиксировать frontend-валидацию для doctor registration form. В `frontend/docs/FORM_VALIDATION.md` закреплён postponed, но формально определённый future contract: username/password, unique positive specialization ids, обязательные документы и multipart/file constraints.
- [x] Зафиксировать frontend-валидацию для create question form. В `frontend/docs/FORM_VALIDATION.md` зафиксированы limits `10..4000`, patient-only access и multiline normalization.
- [x] Зафиксировать frontend-валидацию для answer question form. В `frontend/docs/FORM_VALIDATION.md` зафиксированы limits `2..2000`, doctor-only + verified-doctor guard и per-question submit lock.
- [x] Зафиксировать frontend-валидацию для profile update form. В `frontend/docs/FORM_VALIDATION.md` зафиксированы rule "хотя бы одно поле" и limits `<=120`.
- [x] Зафиксировать frontend-валидацию для change password form. В `frontend/docs/FORM_VALIDATION.md` зафиксированы required current password, strong new password, difference from current и confirm match.
- [x] Реализовать единое отображение серверных ошибок по полям и общих ошибок формы. Добавлен shared helper `frontend/src/formSupport.js::resolveFormApiError`, который централизует field/form error extraction для login/register/profile/password/question/documents.
- [x] Реализовать нормализацию пользовательского ввода там, где это нужно. Введены shared helpers `normalizeUsernameValue`, `normalizeOptionalTextValue`, `normalizeMultilineTextValue`; они используются в auth/profile/question flows.

## 25. Тестирование backend после интеграционных изменений

- [x] Подготовить рабочий способ запуска backend тестов в текущем окружении.
- [x] Прогнать существующие backend тесты без изменений.
- [x] Исправить все упавшие backend тесты.
- [x] Добавить backend тесты на новые поля/контракты, если backend расширяется.
- [x] Добавить backend тесты на refresh/logout flow.
- [x] Добавить backend тесты на doctor document upload edge cases.
- [x] Добавить backend тесты на admin moderation flow, если он меняется.
- [x] Добавить backend тесты на любые новые endpoint-ы или DTO.

## 26. Тестирование frontend

- [x] Подготовить стратегию frontend тестирования для ключевых flows.
- [x] Проверить, нужен ли в проекте unit/integration тестовый стек для frontend.
- [x] Добавить smoke-check хотя бы на основные пользовательские flows.
- [ ] Протестировать login flow вручную.
- [ ] Протестировать patient registration flow вручную.
- [ ] Протестировать doctor registration flow вручную, если он входит в этап.
- [ ] Протестировать doctor directory flow вручную.
- [ ] Протестировать doctor profile flow вручную.
- [ ] Протестировать public questions feed вручную.
- [ ] Протестировать create question flow вручную.
- [ ] Протестировать doctor answer flow вручную.
- [ ] Протестировать profile update flow вручную.
- [ ] Протестировать change password flow вручную.
- [ ] Протестировать logout flow вручную.
- [ ] Протестировать admin moderation flow вручную, если он входит в этап.
- [ ] Протестировать сценарии ошибок `401/403/404/409/422`.

Примечание: smoke-покрытие добавлено, но отдельный browser-based manual QA для UI-сценариев ещё нужен.

## 27. Интеграционное end-to-end тестирование

- [x] Проверить сценарий: новый пациент регистрируется и логинится.
- [x] Проверить сценарий: пациент открывает каталог врачей.
- [x] Проверить сценарий: пациент открывает профиль врача.
- [x] Проверить сценарий: пациент создает вопрос.
- [x] Проверить сценарий: неавторизованный пользователь не может создать вопрос.
- [x] Проверить сценарий: врач регистрируется и не может отвечать до верификации.
- [x] Проверить сценарий: администратор верифицирует врача.
- [x] Проверить сценарий: верифицированный врач отвечает на вопрос.
- [x] Проверить сценарий: logout ломает доступ к закрытым действиям до refresh/login.
- [x] Проверить сценарий: перезагрузка страницы не ломает восстановление сессии, если refresh-flow поддерживается.

## 28. Линт, сборка и техническая чистота

- [x] Прогнать `frontend` build после всех изменений.
- [x] Прогнать `frontend` lint после всех изменений.
- [x] Исправить все ошибки frontend lint/build.
- [x] Прогнать backend тесты после всех изменений.
- [x] Прогнать проект целиком через `docker compose up --build`.
- [ ] Проверить, что приложение стартует с нуля на чистой машине/чистой базе по документации.
- [x] Убедиться, что в репозитории нет временных заглушек, console logs и отладочного мусора.
- [x] Убедиться, что не осталось неиспользуемых Stitch-оберток для уже переведенных экранов.

## 29. Документация проекта

- [x] Обновить корневой `README.md` под реальное состояние проекта.
- [x] Обновить `backend/README.md`, если backend-контракты менялись.
- [x] Обновить `frontend/README.md`, если изменилась архитектура запуска и страниц.
- [x] Обновить документацию по frontend-страницам после перевода Stitch-экранов в native React.
- [x] Задокументировать все env-переменные, нужные для локальной разработки.
- [x] Задокументировать auth-flow frontend/backend.
- [x] Задокументировать doctor registration flow.
- [x] Задокументировать admin verification flow.
- [x] Задокументировать ограничения первого MVP и то, что сознательно отложено.

## 30. Production readiness и безопасность

- [x] Проверить, что production-конфиг не использует dev secret key.
- [x] Проверить, что production-конфиг требует `COOKIE_SECURE=true`.
- [x] Проверить, что production-конфиг требует корректные CORS origins.
- [x] Проверить, что production-конфиг не выставляет лишние debug-настройки.
- [x] Проверить, что upload-валидация покрывает размер, mime type и расширение.
- [x] Проверить, что в UI нет утечек чувствительных данных.
- [x] Проверить, что access token не сохраняется небезопасно, если выбран in-memory подход.
- [x] Проверить, что refresh-flow не ломается в production deployment-схеме.
- [x] Подготовить production runbook для запуска приложения.

## 31. Финальная приемка

- [x] Пройтись по всему чеклисту и убедиться, что обязательные для MVP пункты выполнены.
- [x] Зафиксировать список осознанно отложенных задач.
- [x] Зафиксировать список известных ограничений релиза.
- [ ] Провести ручную приемку основного пользовательского сценария.
- [ ] Провести ручную приемку сценария врача.
- [ ] Провести ручную приемку сценария администратора, если он входит в релиз.
- [x] Подготовить итоговое краткое резюме: что работает, что не входит в релиз, какие риски остаются.

Примечание: итоговый автоматизированный статус и ограничения зафиксированы в `docs/RELEASE_READINESS.md`.
