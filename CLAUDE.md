# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current repository state

- This repository now contains a verified runnable MVP implementation under `apps/api`, `apps/web`, `deploy/docker`, and `tests`.
- Root collaboration files exist: `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `PRIVACY.md`, `LICENSE`, `.github/PULL_REQUEST_TEMPLATE.md`.
- Treat the `docs/` tree as the current source of truth for product scope and frozen contracts, but verify code paths and commands against the checked-in implementation before making delivery claims.

## Source-of-truth reading order

When you need project context, read in this order:

1. `README.md` — repo status, MVP loop, and top-level constraints.
2. `docs/README.md` — canonical reading order for the split documentation system.
3. `docs/01-product/*.md` — scope, requirements, user journeys, and functional/non-functional expectations.
4. `docs/02-architecture/*.md` and `docs/02-architecture/adr/*.md` — system boundaries, API contract, data model, security, observability, and frozen architecture decisions.
5. `docs/03-delivery/*.md` and `docs/05-review/*.md` — scaffold-ready delivery specs, interface freeze, testing/deployment/release plans, acceptance gates, and review rules.
6. Historical inputs for background only: `Digital Avatar 正式方案 V14.md`, `Digital Avatar 正式方案 V13.md`, `总体设计方案.md`, `docs/minimax多智能体评审意见.md`, `docs/frontend-architecture-review.md`.

If a user asks for a change to a frozen decision, also check `docs/00-governance/decision-log.md` and the affected ADRs.

## Commands

Verified commands currently available in this repository:

- Backend dev server: `cd apps/api && python3 -m uvicorn app.main:app --reload --port 8000`
- Backend tests: `cd apps/api && python3 -m pytest`
- Frontend dev server: `cd apps/web && npm run dev`
- Frontend tests: `cd apps/web && npm run test -- --run`
- Frontend build: `cd apps/web && npm run build`
- Docker Compose: `cd deploy/docker && docker compose up --build`

Before suggesting any additional command, verify it against the actual manifests in the repo (`apps/api/pyproject.toml`, `apps/web/package.json`, `deploy/docker/docker-compose.yml`, `.github/workflows/*.yml`).

## Big-picture architecture

The planned system is a layered digital-avatar platform organized around domain boundaries rather than UI pages:

- **Application layer**: Web Console, REST API, CLI, Docker delivery
- **Domain layer**: User, Avatar, Persona, Agent, Task, Memory, Policy, Audit
- **Service layer**: orchestration, validation, and use-case flows
- **Infrastructure layer**: database, model provider adapter, vector store, file/log persistence
- **Extension layer**: events/modules/integrations; reserved for later, not part of the MVP runtime path

Key architecture rules from `docs/02-architecture/architecture.md`:

- Controllers/routes should not contain core business logic.
- The main business path is synchronous service orchestration; async is for long-running execution and non-critical side effects.
- Module boundaries are domain-oriented: Auth, Avatar, Persona, Agent, Task, Memory, Policy, Audit, Provider.
- MVP freezes interfaces and responsibilities for extension points, but does not include a real dynamic plugin runtime.

## Main product loop

The MVP is intentionally narrow and centers on one end-to-end loop:

1. User logs in and creates an Avatar.
2. User imports minimal material and generates a Persona.
3. User creates a default Agent.
4. User executes a Task.
5. System captures candidate memories.
6. User confirms or rejects those memories before long-term persistence.
7. System records policy decisions and append-only audit data across the flow.

When evaluating scope, prefer decisions that strengthen this loop instead of expanding into adjacent features.

## Core domain model

The planned persistent model revolves around these entities:

- `User`
- `Avatar`
- `Persona`
- `Agent`
- `Task`
- `Memory`
- `Policy`
- `AuditLog`
- `Module`

Important invariants from the docs:

- `Persona` is a stable profile summary; `Memory` is a discrete, searchable long-term item.
- MVP does **not** support agent-private long-term memory; memory is Avatar-scoped.
- `Module` is a declaration/whitelist concept in MVP, not an active plugin runtime.
- Memory persistence is confirmation-based by default.

Memory lifecycle:

- `captured -> pending_confirm -> confirmed -> archived`
- `captured -> pending_confirm -> rejected`

## Main execution flow

The core task path is:

`Create Task -> Pre-Policy Check -> Assemble Context -> Invoke Provider -> Post-Policy Check -> Persist Result -> Capture Candidate Memories -> Append Audit Log -> Return Task Status`

This means task orchestration code should remain the place where Persona injection, memory recall, policy checks, provider invocation, memory capture, and audit writes are coordinated.

## API and contract expectations

The planned public API is REST-first under `/api/v1`.

Key contract decisions already frozen in docs:

- Unified error shape with `error.code`, `message`, `trace_id`, and `details`
- Async semantics for task execution: task creation returns a task shell, then callers poll/read task state
- Default pagination for list endpoints
- `trace_id` is part of critical write and audit flows
- Memory search should not return full sensitive content by default

If implementation work begins, keep controller/route layers thin and place business logic in service/domain layers.

## Planned implementation shape

The intended scaffold is now largely present in the repository:

- Backend: `apps/api/` with route/service/schema/model/worker separation
- Frontend: `apps/web/` with `api/`, `types/generated/`, `stores/`, `views/`, and `router/`
- Tests: `tests/unit`, `tests/integration`, `tests/e2e`, `tests/security`, `tests/smoke`
- Ops: `deploy/docker/` plus Compose and Dockerfiles

When making changes, prefer aligning implementation and docs to the existing checked-in structure rather than treating these paths as hypothetical.

## Frozen technical decisions worth preserving

From the decision log and ADRs:

- SQLite + `sqlite-vec` is the MVP storage/vector choice; Chroma is deferred.
- Task execution is modeled asynchronously.
- Frontend stack is frozen to Vue 3 + Vite + TypeScript strict + Pinia + Vue Router 4 + Axios.
- OpenAPI-generated frontend types are the intended source of truth for DTOs.
- Authentication is JWT + refresh token.
- Candidate memories must not be auto-promoted into long-term memory without user confirmation.
- Parallel development assumes API, error codes, domain states, and audit structure are frozen first.

## Documentation change rules

This repository’s main work product is its documentation set. When changing docs:

- Prefer editing the split docs under `docs/` instead of expanding the legacy monolithic proposal files.
- Keep current normative docs separate from historical inputs.
- If you change a frozen contract, update all linked artifacts together, typically including:
  - `docs/00-governance/decision-log.md`
  - relevant ADRs under `docs/02-architecture/adr/`
  - `docs/03-delivery/interface-freeze-checklist.md`
  - affected delivery/review docs such as testing, quality gates, acceptance, or deployment docs
- Use `CONTRIBUTING.md` and `.github/PULL_REQUEST_TEMPLATE.md` as the contribution/review baseline for PR-shaped changes.

## Frontend-specific guidance

The frontend docs already freeze several important implementation choices:

- Use Pinia, not Vuex.
- Use OpenAPI generation as the only source for frontend API types.
- Keep API access centralized in `api/client.ts` with auth headers, error interception, and `trace_id` propagation.
- Use `AbortController` for cancellation-sensitive views.
- Expose policy-blocked states and `trace_id` clearly in the UI.

## Deployment and testing guidance

The repository now includes an executable MVP stack:

- Deployment target: single-machine Docker Compose with `web`, `api`, `worker`, and optional `ollama`
- Runtime ports: web `4173`, api `8000`, ollama `11434`
- Health model: `GET /health` plus provider health under `/api/v1/provider/health`
- Testing layers present: unit, integration, e2e, security, smoke
- CI workflows exist under `.github/workflows/ci.yml` and `.github/workflows/e2e.yml`

Keep docs and implementation aligned. If commands, ports, or workflow gates change, update both the code and the delivery/review docs together.
