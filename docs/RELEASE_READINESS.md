# Release Readiness

## Verified on 2026-03-11

- backend tests: `22 passed`
- frontend smoke tests: `4 passed`
- frontend lint: passed
- frontend build: passed
- `docker compose up --build`: passed
- backend health via published port: `200 OK`
- frontend HTTP response via published port: `200 OK`

## Automated flows covered

- patient registration and login
- refresh rotation and logout
- session restore from refresh cookie after a reload-style re-entry
- doctor registration backend contract
- doctor document upload edge cases
- admin moderation queue, doctor detail, document download, verify/unverify
- public doctor directory and doctor public profile
- patient question creation
- unauthorized question creation rejection
- verified doctor answer flow
- production config guardrails for secret key, secure cookies, CORS, and disabled docs

## Deferred manual QA

The following still require a browser-based manual pass before public release sign-off:

- login UI flow
- patient registration UI flow
- doctor directory UI flow
- doctor profile UI flow
- public questions feed UI flow
- create question UI flow
- doctor answer UI flow
- profile update UI flow
- change password UI flow
- logout UI flow
- admin moderation UI flow
- browser validation of `401/403/404/409/422` presentation

## Known release limitations

- doctor self-registration UI is postponed; only the backend endpoint is available in this iteration
- frontend uses smoke-level automated coverage, not a full browser E2E stack
- clean-machine verification was performed on the current workstation through Docker Compose startup, not on a brand-new host

## Short summary

What works:

- the backend contracts for auth, moderation, uploads, doctor/public data, and Q&A are green under tests;
- the frontend builds cleanly, passes lint, and has smoke coverage for critical client auth/routing behavior;
- the Docker Compose stack starts and answers on the published backend/frontend ports.

What is not in the release yet:

- native public doctor registration UI;
- full browser E2E automation;
- final human sign-off of all user-facing flows in the browser.

Main remaining risks:

- last-mile UI issues that only appear in a real browser interaction pass;
- production deployment mistakes around cookie domain/samesite/cors if the runbook is not followed exactly.
