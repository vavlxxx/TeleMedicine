# Production Runbook

## Preconditions

- build and tests are green:
  - `docker compose run --rm backend-test poetry run python -m pytest`
  - `cd frontend && npm run test:smoke && npm run lint && npm run build`
- production backend env is prepared outside the repository.
- HTTPS and a real public frontend origin are available.

## Required backend production env

At minimum configure:

- `CFG_APP__MODE=PROD`
- `CFG_DB__HOST`
- `CFG_DB__PORT`
- `CFG_DB__USER`
- `CFG_DB__PASSWORD`
- `CFG_DB__NAME`
- `CFG_AUTH__SECRET_KEY=<long random secret>`
- `CFG_AUTH__COOKIE_SECURE=true`
- `CFG_AUTH__COOKIE_SAMESITE=none` when frontend and backend are on different sites
- `CFG_AUTH__COOKIE_DOMAIN=<shared cookie domain when required>`
- `CFG_CORS__ALLOWED_ORIGINS=<real frontend origin list>`
- `CFG_APP__DOCS_URL=null`
- `CFG_APP__REDOC_URL=null`
- `CFG_APP__OPENAPI_URL=null`
- `CFG_BOOTSTRAP__SUPERUSER_USERNAME`
- `CFG_BOOTSTRAP__SUPERUSER_PASSWORD`

## Required frontend production env

- `VITE_API_BASE_URL=/api/v1` when frontend is served behind the same origin/proxy
- or configure a production-safe proxy/reverse proxy that forwards `/api` to backend

## Deployment sequence

1. Prepare production env files or secret injection for backend and postgres.
2. Build images:

```bash
docker compose build backend frontend
```

3. Start the stack:

```bash
docker compose up -d postgres backend frontend
```

4. Wait for backend health:

```bash
curl -i http://<backend-host>/health
```

5. Verify frontend entrypoint:

```bash
curl -I http://<frontend-host>/
```

## Post-deploy smoke checks

- patient registration and login succeed;
- page reload restores session through refresh flow;
- logout clears access to protected actions until the next login;
- admin can open moderation queue and verify a doctor;
- verified doctor can answer in the Q&A feed;
- public doctor directory and public doctor profile stay accessible anonymously.

## Refresh-flow deployment rules

- frontend requests must use `credentials: include`;
- backend CORS must allow the exact frontend origin and credentials;
- refresh cookie must be `Secure` in production;
- if frontend/backend are on different sites, cookie `SameSite` must allow the chosen deployment topology.

## Upload safety checks

Doctor document uploads are expected to stay constrained by:

- max file count;
- max file size;
- allowed extensions;
- allowed MIME types.

Do not widen these lists in production without updating moderation and storage policies.

## Rollback

1. Stop frontend traffic to the new deployment.
2. Re-deploy the previous backend/frontend images.
3. Keep the same database unless the failed deployment included a backward-incompatible migration.
4. Re-run health and auth smoke checks.
