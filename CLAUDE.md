# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current repository state

- This repository contains a runnable MVP under `apps/api`, `apps/web`, `deploy/docker`, and `tests`.
- Treat `docs/` as the source of truth for product scope and frozen contracts, but verify commands and behavior against the checked-in implementation before making delivery claims.
- There are no checked-in Cursor rules or Copilot instruction files in this repository.

## Source-of-truth reading order

When you need project context, read in this order:

1. `README.md` — current repo status, MVP loop, and local run modes.
2. `docs/README.md` — canonical reading order for the split documentation system.
3. `docs/01-product/*.md` — scope, requirements, user journeys, and functional expectations.
4. `docs/02-architecture/*.md` and `docs/02-architecture/adr/*.md` — architecture, API contracts, data model, security, observability, and frozen decisions.
5. `docs/03-delivery/*.md` and `docs/05-review/*.md` — interface freeze, testing, deployment, release, and acceptance criteria.
6. Historical inputs only for background: `Digital Avatar 正式方案 V14.md`, `Digital Avatar 正式方案 V13.md`, `总体设计方案.md`, `docs/minimax多智能体评审意见.md`, `docs/frontend-architecture-review.md`.

If a requested change touches a frozen decision, also check `docs/00-governance/decision-log.md` and the relevant ADRs.

## Common commands

Verify any new command against the checked-in manifests before suggesting it.

### Backend (`apps/api`)

- Install dependencies: `cd apps/api && pip install .[dev]`
- Run dev server: `cd apps/api && python3 -m uvicorn app.main:app --reload --port 8000`
- Run all backend tests: `cd apps/api && python3 -m pytest`
- Run one test file: `cd apps/api && python3 -m pytest ../../tests/integration/test_api.py`
- Run one test case: `cd apps/api && python3 -m pytest ../../tests/security/test_memory_policy.py -k reject`
- Compile-check backend package: `cd apps/api && python3 -m compileall app`

### Frontend (`apps/web`)

- Install dependencies: `cd apps/web && npm ci`
- Run dev server: `cd apps/web && npm run dev`
- Build production bundle: `cd apps/web && npm run build`
- Run all frontend tests: `cd apps/web && npm run test -- --run`
- Run one frontend test file: `cd apps/web && npm run test -- src/stores/auth.spec.ts --run`
- Regenerate OpenAPI types from the backend app: `cd apps/web && npm run generate:types`
- Verify generated OpenAPI artifacts are up to date: `cd apps/web && npm run check:types`

### Docker / end-to-end

- Start local stack: `cd deploy/docker && docker compose up --build`
- Validate Compose config: `docker compose -f deploy/docker/docker-compose.yml config`
- Run compose smoke test: `python3 -m pytest tests/smoke/test_compose_stack.py -v`
- Run HTTP E2E test against a running API: `cd apps/api && python3 -m pytest ../../tests/e2e/test_smoke.py -v`

## Big-picture architecture

The repository implements a narrow MVP around one main loop: login -> create avatar -> generate persona -> create agent -> execute task -> review candidate memories -> inspect audit trail.

### Backend shape

- FastAPI app entrypoint: `apps/api/app/main.py`.
- API routes are mounted under `/api/v1` via `apps/api/app/api/v1/router.py`.
- Route handlers stay thin; business logic lives in `apps/api/app/services/`.
- SQLAlchemy models live in `apps/api/app/models/models.py`; DB session setup is in `apps/api/app/db/session.py`.
- The app currently creates tables at startup and seeds a demo user through `lifespan`/bootstrap code rather than running Alembic migrations on boot.

Important service boundaries:

- `services/auth.py` handles login, refresh, and token issuance.
- `services/tasks.py` is the core orchestrator: pre-policy check, context assembly, provider call, post-policy check, memory capture, and audit append.
- `services/provider.py` wraps model access and switches between `mock` and `live` provider behavior.
- `services/memories.py` enforces candidate-memory confirmation/rejection transitions.
- `services/audit.py` writes append-only hash-chained audit records.

### Actual task execution model

The documented architecture talks about asynchronous task execution, but the checked-in implementation is important to understand:

- `POST /tasks` creates a task shell, then starts background execution from the API process.
- The frontend polls task status until it reaches a terminal state.
- A separate `worker` entrypoint/container exists, but there is no broker-backed durable queue in the current implementation.

When changing task behavior, treat `services/tasks.py` as the coordination point for persona injection, memory recall/capture, provider invocation, policy checks, persistence, and audit logging.

### Domain model and invariants

Core persisted entities are `User`, `Avatar`, `Persona`, `Agent`, `Task`, `Memory`, and `AuditLog`.

Key invariants that show up in both docs and code:

- `Persona` is a stable profile summary; `Memory` is a discrete long-term item.
- Long-term memory is avatar-scoped, not agent-private.
- Candidate memories default to pending confirmation and must not be auto-promoted.
- Task records carry `trace_id`, result/error fields, and terminal status.
- Audit records are append-only and hash chained.

## Frontend architecture

The frontend is a Vue 3 + Vite + TypeScript + Pinia + Vue Router application.

- App bootstrap is in `apps/web/src/main.ts`.
- Global shell and navigation live in `apps/web/src/App.vue`.
- Routing is centralized in `apps/web/src/router/index.ts`.
- Shared API access is centralized in `apps/web/src/api/client.ts` and `apps/web/src/api/index.ts`.
- State is store-driven: auth, avatar context, and workspace/task/memory loading live in Pinia stores under `apps/web/src/stores/`.

Important frontend patterns:

- Axios client injects bearer auth and `x-trace-id`, and retries once on 401 after refresh.
- The UI reflects backend async semantics by creating a task, polling for completion, then refreshing pending memories and audit data.
- Generated OpenAPI types are intended to be the frontend DTO source of truth; if backend schemas change, regenerate types and keep generated artifacts in sync.

## Testing and delivery model

Test layers present in the repo:

- Backend unit, integration, security, and smoke tests are configured from `apps/api/pyproject.toml` and live under `tests/`.
- Frontend tests use Vitest and focus on stores and UI behavior.
- CI in `.github/workflows/ci.yml` runs API tests, web type verification/tests/build, and a Docker smoke stack.
- `.github/workflows/e2e.yml` separately boots the API and runs HTTP E2E smoke coverage.

## Deployment notes

- Docker Compose lives in `deploy/docker/docker-compose.yml` and brings up `api`, `worker`, `web`, and optional `ollama`.
- Default local ports are web `4173`, api `8000`, ollama `11434`.
- Compose currently forces `PROVIDER_MODE=mock` for `api` and `worker`; do not assume live model access unless env/config has been changed deliberately.
- `README.md` documents helper scripts under `deploy/docker/ops/scripts/` and the current local provider expectations.

## Documentation update rules

This repository’s docs are a maintained deliverable, not just background notes.

- Prefer updating split docs under `docs/` rather than legacy monolithic proposal files.
- Keep current normative docs separate from historical inputs.
- If you change a frozen contract, update linked artifacts together, typically including:
  - `docs/00-governance/decision-log.md`
  - relevant ADRs in `docs/02-architecture/adr/`
  - `docs/03-delivery/interface-freeze-checklist.md`
  - affected testing, deployment, review, and acceptance docs
- Keep implementation and docs aligned when changing commands, ports, workflows, or runtime behavior.
