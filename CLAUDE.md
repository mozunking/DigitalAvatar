# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current repository state

- The repository currently contains a single project design document: `总体设计方案.md`.
- There is no checked-in application code, package manifest, lockfile, CI config, or runnable project scaffold yet.
- Before suggesting build, lint, or test commands, verify whether the implementation has been added; do not assume the planned stack is already present.

## Existing source of truth

- `总体设计方案.md` is the current authoritative project proposal for the initial architecture, MVP scope, API surface, and delivery plan.
- Treat the document as design intent, not proof that files, modules, or commands already exist.

## Expected architecture from the proposal

The design document describes a layered digital-avatar agent system with four major layers:

1. **Application layer**: Web Console, REST API, CLI, Docker delivery.
2. **Domain layer**: Avatar, Agent, Memory, and Policy domains.
3. **Infrastructure layer**: LLM provider integration, DB, vector store, and audit persistence.
4. **Runtime/extension layer**: Event bus, module loader, and task worker.

Planned domain entities and responsibilities:

- **Avatar**: top-level digital persona container for a user.
- **Persona**: generated style/profile summary derived from imported user material.
- **Agent**: task-executing sub-agent with a role, system prompt, and permissions.
- **Task**: execution unit run by an agent with traceable status/result.
- **Memory**: typed memory records with confirmation workflow.
- **Policy**: rule definitions for safety, boundary enforcement, and blocking.
- **AuditLog**: append-only audit trail with hash-chain style integrity fields.
- **Module**: extension unit loaded through a whitelist/module system.

## Planned main workflow

The MVP is centered on one end-to-end loop:

1. Create an avatar.
2. Import user material / dialogue samples.
3. Generate a Persona/Profile.
4. Create one task agent.
5. Execute a task with Persona + recalled Memory in context.
6. Capture candidate memories from execution.
7. Require user confirmation before long-term memory persistence.
8. Record policy checks and audit logs across the flow.

## Planned module boundaries

If/when the implementation is created, align work with these boundaries from the proposal instead of organizing around UI pages:

- **Provider layer**: `chat`, `stream_chat`, `embed`, `health_check`, `model_info`.
- **Agent orchestration**: task intake, context assembly, Persona injection, memory recall, model invocation, result shaping, memory capture trigger, audit writes.
- **Memory service**: capture, pending list, confirm/reject, search, archive, delete.
- **Policy & Audit**: inbound/outbound/task/tool validation, risk blocking, audit append.
- **Event bus**: notifications, async audit, extension hooks; not the primary business-call path.
- **Module loader**: whitelist registration, enable/disable, manifest permissions.

## Planned storage model

The proposal expects SQLite first, with a later path to PostgreSQL. Core tables described in the design doc:

- `users`
- `avatars`
- `personas`
- `agents`
- `tasks`
- `memories`
- `policies`
- `audit_logs`
- `modules`

Memory records are designed to follow this state flow:

- `captured -> pending_confirm -> confirmed -> archived`
- `captured -> pending_confirm -> rejected`

## Planned API surface

The proposal defines a REST-first API under `/api/v1`, including:

- Avatar creation and lookup
- Persona generation and latest Persona retrieval
- Agent creation and lookup
- Task creation/execution and status retrieval
- Pending memory listing, memory confirm/reject, memory search
- Policy check and policy list
- Audit log list/detail
- Module list and enable/disable operations

When implementation begins, keep route/service separation clear and avoid placing business logic directly in controllers.

## Planned technology choices

These are proposal-level defaults, not verified repo reality:

- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy
- **Frontend**: Vue 3, Vite, TypeScript, Element Plus
- **Storage**: SQLite plus a vector store such as Chroma / FAISS / sqlite-vec
- **Model runtime**: Ollama first for MVP; Anthropic/OpenAI later in Beta
- **Testing**: Pytest, Vitest, Playwright
- **Delivery**: Docker

## Commands

There are currently no verified build, lint, or test commands in the repository because no runnable project scaffold is checked in yet.

Once implementation exists, future Claude instances should inspect the real manifests/config files before adding commands here, especially:

- `package.json`
- `pyproject.toml`
- `requirements*.txt`
- `docker-compose.yml`
- `Makefile`
- CI workflow files

Do not invent commands from the proposal alone.

## Working guidance for future edits

- Verify whether a requested change should modify the proposal document or actual implementation files; right now only the proposal exists.
- If scaffolding the repo from the design doc, preserve the domain-oriented boundaries above rather than collapsing everything into one app layer.
- Keep policy/audit enforcement embedded at critical entry points, as specified in the proposal.
- Keep memory persistence confirmation-based; candidate memories should not be written directly as durable long-term memory by default.
- Treat plugin/module execution as whitelist-first with explicit permission declarations.

## Frontend Architecture Review (V12)

A comprehensive frontend architecture review has been completed. Key findings and guidance:

### Technology Stack Assessment
- **Vue 3 + Vite + TypeScript (strict)**: Recommended, solid choice
- **Element Plus**: Good for enterprise use, but configure tree-shaking for bundle optimization
- **Missing**: Pinia (state management), Vue Router 4 (routing), Axios/ky (HTTP client)

### Recommended Frontend Stack
```json
{
  "framework": "Vue 3 + Composition API",
  "build": "Vite",
  "language": "TypeScript (strict)",
  "state": "Pinia",
  "routing": "Vue Router 4",
  "http": "Axios",
  "ui": "Element Plus (with tree-shaking)",
  "testing": "Vitest + Playwright"
}
```

### Frontend Directory Structure (Recommended)
```
apps/web/src/
├── api/           # API layer: HTTP requests
├── types/         # Type definitions (consider OpenAPI auto-generation)
├── stores/        # Pinia stores (domain-oriented)
├── composables/   # Reusable composition functions
├── components/    # Components (common/ + domain/)
├── views/         # Page components
├── router/        # Vue Router config
└── utils/         # Pure utility functions
```

### Priority Improvements
**P0 (Must do before implementation):**
- Define Pinia as state management solution
- Add Login/Auth page (missing in current proposal)
- Add Avatar List page (missing in current proposal)
- Configure Element Plus tree-shaking via unplugin-vue-components

**P1 (Should do for MVP quality):**
- API type auto-generation mechanism (OpenAPI)
- Task execution page with SSE real-time status
- Global error handling and loading states
- CSRF/XSS security configuration

**P2 (Nice to have for Beta):**
- Responsive design refinement
- Accessibility improvements (WCAG AA)
- Performance monitoring

### MVP Pages (Updated)
Based on review, recommend these pages for MVP:
1. Login/Auth page
2. Home/Dashboard
3. Avatar List page
4. Avatar Create page
5. Persona Generate page
6. Agent Management page
7. Task Execution page
8. Pending Memory Confirm page
9. Memory Search page
10. Audit Log page
11. Settings page
12. 404/Error page

### Key Frontend Decisions to Make
1. **State Management**: Use Pinia (Vue 3 official), NOT Vuex
2. **API Types**: Generate from OpenAPI spec, not manual maintenance
3. **Error Handling**: Global Axios interceptor + error boundary components
4. **Request Cancellation**: Use AbortController for tab switching scenarios
5. **Real-time Updates**: Consider SSE for task status (vs polling)
