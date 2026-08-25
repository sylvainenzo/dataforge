# DataForge — Phase 1: Product & Technical Architecture

**Status:** Draft for approval — no implementation code has been written.
**Scope note:** No pre-existing UI/UX design was supplied for this project (verified: the referenced TikTok link is a video with no fetchable design content). Per your direction, the UI/UX sections below are an **original proposed design system**, not an extraction of a supplied design. Everything in this document is labeled `[FACT]`, `[RECOMMENDATION]`, `[ASSUMPTION]`, or `[EXAMPLE]` where the distinction matters.

---

## 1. Product Specification

**Product:** DataForge — an interactive Data Science & Analytics learning platform taking a learner from zero programming knowledge to professional-level Data Analytics / Data Science / ML capability.

**Core loop:** Learn → Understand → Interact → Practice → Code → Solve → Get Feedback → Build → Review → Master.

**Primary surfaces (v1 scope vs. later):**

| Surface | v1 (Phases 1–15) | Post-v1 |
|---|---|---|
| Curriculum (lessons, quizzes) | ✅ | — |
| Python Lab (Pyodide, client-side) | ✅ | — |
| SQL Lab (isolated Postgres schemas) | ✅ | — |
| Statistics/Math interactive simulations | ✅ | — |
| Server-side Python execution (ML/heavier workloads) | ✅ (single-node sandbox pool) | Autoscaled sandbox fleet |
| R Lab | `[ASSUMPTION]` Phase 8 stretch — same sandbox mechanism as Python, lower priority | Full parity |
| AI Tutor | ✅ (RAG + Claude API) | Fine-tuned personalization |
| Dataset library + EDA lab | ✅ | Big-data (Spark) tier |
| Data Visualization builder | ✅ | — |
| Project Factory / Capstones | ✅ | — |
| Mac Setup Wizard | ✅ | Windows/Linux wizard |
| Gamification, spaced repetition, certificates | ✅ | — |
| Admin dashboard | ✅ | — |
| BI tool integration (Power BI/Tableau embeds) | `[RECOMMENDATION]` link out to official tools; do not attempt to reimplement Power BI/Tableau in-browser | — |

**Non-goals for v1** `[RECOMMENDATION]`: real GPU-backed deep learning training in-browser, Spark/Kafka live clusters, mobile native apps, multi-tenant white-labeling. These are explicitly out of scope so the platform ships something real rather than a half-built version of everything.

---

## 2. System Architecture Overview

**Recommended shape:** a **modular monolith** for the core platform, plus **one isolated service** for anything that executes untrusted user code, plus a **separate SPA frontend**. This is elaborated in §3.

**Text architecture diagram:**

```
                                   ┌─────────────────────┐
                                   │        Users         │
                                   └──────────┬───────────┘
                                              │ HTTPS
                                   ┌──────────▼───────────┐
                                   │   Reverse Proxy (Traefik) │
                                   │   TLS termination, routing │
                                   └──────────┬───────────┘
                     ┌────────────────────────┼─────────────────────────┐
                     │                        │                         │
           ┌─────────▼─────────┐   ┌──────────▼──────────┐   ┌──────────▼──────────┐
           │   Frontend (SPA)   │   │   Core API (FastAPI  │   │  Execution Gateway   │
           │  React/Vite static │   │   modular monolith)  │   │  (WS + REST, thin)   │
           │  served via CDN/   │   │  auth·curriculum·    │   └──────────┬──────────┘
           │  proxy             │   │  progress·ai-tutor·  │              │
           └────────────────────┘   │  datasets·admin·…    │   ┌──────────▼──────────┐
                                     └───┬────────┬────────┘   │  Sandbox Orchestrator │
                                         │        │            │  (spawns/kills         │
                              ┌──────────▼──┐  ┌──▼─────────┐  │  ephemeral gVisor      │
                              │ PostgreSQL  │  │   Redis     │  │  containers)           │
                              │ (+pgvector) │  │ cache/queue │  └──────────┬──────────┘
                              └─────────────┘  └──┬──────────┘             │
                                                   │                ┌──────▼───────┐
                                         ┌─────────▼────────┐       │ Ephemeral      │
                                         │  Celery Workers   │       │ Sandbox Pods   │
                                         │  (EDA, email,     │       │ (Python/R/SQL  │
                                         │  certs, embeddings│       │  per-session,  │
                                         │  spaced-rep jobs) │       │  no net, no fs │
                                         └────────────────────┘       │  persistence)  │
                                                                       └───────────────┘
                              ┌─────────────┐
                              │  S3/MinIO   │  ← datasets, uploads, certificates, exports
                              └─────────────┘
```

**Component summary:**

| Component | Responsibility | Talks to |
|---|---|---|
| Frontend SPA | All UI, Monaco/xterm/Pyodide client-side execution for light exercises | Core API, Execution Gateway (WS) |
| Core API | Everything that is *not* running untrusted code: auth, curriculum, quizzes, progress, gamification, AI tutor orchestration, datasets metadata, admin, search, career, certificates | Postgres, Redis, S3, Execution Gateway (internal), Claude API |
| Execution Gateway | Thin, stateless entrypoint that authenticates a user's run request, applies rate limits/quotas, and hands off to the orchestrator | Sandbox Orchestrator |
| Sandbox Orchestrator | Spins up/tears down ephemeral, resource-limited, network-isolated containers per run; streams stdout/stderr back over WS | Ephemeral sandbox containers |
| Celery Workers | Async/long-running jobs: large dataset profiling, certificate PDF generation, embedding generation for AI tutor RAG, spaced-repetition scheduling, transactional email | Postgres, Redis, S3 |
| PostgreSQL | System of record for everything (see §6). `pgvector` extension for AI tutor RAG embeddings — avoids standing up a separate vector DB at this scale | — |
| Redis | Cache, Celery broker/result backend, rate-limit counters, session/short-lived state | — |
| S3/MinIO | Dataset files, user uploads, generated certificates/exports | — |

---

## 3. Architecture Decision: Modular Monolith vs. Microservices

**Analysis:**

| Factor | Modular monolith | Microservices |
|---|---|---|
| Dev speed (small/solo-to-small team) | High — one deploy, one codebase, no network calls between features | Low — overhead of service boundaries, contracts, deployment coordination |
| Maintainability at this stage | High if modules are cleanly separated internally | Only pays off once teams/domains are large enough to need independent deploys |
| Security isolation | Fine for everything **except** code execution | Natural fit for the one place that actually needs a hard boundary |
| Scalability | Vertical + read replicas + worker scaling covers this platform's realistic load for a long time | Needed only when specific components (e.g., execution) must scale independently — which is true here, just for one component |
| Cost/ops complexity | Low: one Postgres, one Redis, one deploy pipeline | High: service mesh, multiple deploy pipelines, distributed tracing needed just to debug |
| Team size (`[ASSUMPTION]` small founding team) | Matches | Mismatches — microservices tax is paid before there's a team to justify it |

**Recommendation `[RECOMMENDATION]`:** Modular monolith for the Core API, with internal module boundaries strict enough (see folder structure §18) that any module *could* be extracted later without a rewrite. The **one deliberate exception** is code execution: it is pulled out into its own service/security boundary from day one, not because of scale, but because it is the one component that runs untrusted input and must never share a process, filesystem, or credentials with the rest of the platform. This satisfies your instruction in §8 directly: don't force microservices everywhere, but do isolate security-sensitive execution.

---

## 4. Frontend Architecture

**Stack:** React 18, TypeScript, Vite, Tailwind CSS, Radix UI primitives + shadcn/ui patterns, Framer Motion, Monaco Editor, TanStack Query (server state), Zustand (genuinely global client state only — e.g. current user, theme, command palette open/closed).

**State management split `[RECOMMENDATION]`:**
- **Server state** (curriculum, progress, datasets, quiz results, AI tutor messages): TanStack Query. Never duplicated into Zustand.
- **Local/component state**: `useState`/`useReducer` — editor buffer contents, form inputs, modal open state.
- **Global client state** (Zustand, kept deliberately small): authenticated user, theme, sidebar collapsed/expanded, command palette, active lab session id.

**Routing:** file-based or centrally-defined route table under `app/routes` (decided in Phase 4), code-split per top-level section (Dashboard, Labs, Courses, Admin, etc.) so the full curriculum is never loaded into one bundle (see §54 performance requirement).

**Folder structure** — see §18.

---

## 5. Backend Architecture

**Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.x (async), Alembic migrations, Pydantic v2 schemas, JWT (access + refresh) via `python-jose`/`authlib`, OAuth2 (Google, GitHub) via Authlib, WebSockets (FastAPI native) for execution streaming and AI tutor streaming.

**Module boundaries inside the monolith** (each is a Python package under `app/`, each owns its own DB tables and only talks to other modules through its service-layer functions — never reaches into another module's models directly):

`auth`, `curriculum` (courses/modules/lessons/learning-paths), `quizzes`, `labs` (SQL/Python/R/Stats/Math lab metadata — *not* execution itself), `projects`, `datasets`, `ai_tutor`, `progress`, `gamification`, `spaced_repetition`, `career`, `certificates`, `resources` (tools/glossary/research library), `mac_setup`, `search`, `admin`, `notifications`.

**Cross-cutting `core/`:** config, DB session, security (hashing, JWT), rate limiting, logging, exceptions.

**Execution boundary `execution/`:** contains only the *client* used by Core API to talk to the separate Execution Gateway service (over an internal network, service-to-service auth token) — no actual code-running logic lives in the monolith. This is the enforced seam described in §3.

---

## 6. Database Architecture

**Engine:** PostgreSQL 15+ with `pgvector` extension.

**Design principles:** 3NF for transactional tables, explicit FKs with `ON DELETE` policy per relationship (e.g. cascade progress rows when a user is deleted, restrict deletion of a course that has active enrollments), indexes on all FK columns and on columns used in the recommendation/search paths, unique constraints on natural keys (e.g. `(user_id, lesson_id)` on progress rows).

**Table groups** (full column-level schema is Phase 2 deliverable, not this one):

- **Identity:** `users`, `profiles`, `roles`, `oauth_accounts`
- **Curriculum:** `courses`, `modules`, `lessons`, `topics`, `skills`, `learning_paths`, `learning_path_courses`
- **Assessment:** `quizzes`, `quiz_questions`, `quiz_attempts`, `code_submissions`
- **Projects:** `projects`, `project_submissions`
- **Datasets:** `datasets`, `dataset_versions`
- **Knowledge base:** `resources`, `tools`, `install_guides`, `glossary_terms`
- **Career:** `career_paths`, `career_path_skills`
- **Learning science:** `flashcards`, `spaced_repetition_logs`, `user_progress`
- **Gamification:** `achievements`, `badges`, `certificates`
- **AI:** `ai_sessions`, `ai_messages`, `ai_embeddings` (pgvector column)
- **Experiments (ML lab runs):** `experiments`, `model_runs`
- **Platform:** `notifications`, `audit_logs`

This becomes the literal Phase 2 ERD deliverable.

---

## 7. Code Execution Architecture (security-critical)

**Two tiers, matched to workload:**

1. **Client-side (Pyodide/WASM)** — beginner Python exercises: NumPy, pandas basics, simple stats/plots. Runs entirely in the learner's browser. Zero server cost, zero security exposure, but limited to what pure-Python/WASM-compiled packages support and to small data.
2. **Server-side sandbox** — SQL Lab, heavier Python (scikit-learn, model training on course-sized datasets), and (later) R. Every run is a **new ephemeral, gVisor-hardened container** (`runsc` runtime), never a reused process.

`[RECOMMENDATION]` gVisor over Firecracker for the default deployment: Firecracker needs bare-metal/KVM access that most managed hosts don't expose, while gVisor runs as a normal (hardened) container runtime on any Docker/Kubernetes host — easier to operate at this team's scale while still intercepting syscalls. Firecracker becomes the upgrade path if the platform later moves to bare-metal or a provider that supports it (e.g. Fly.io machines).

**Non-negotiable sandbox properties (directly from your spec, restated as enforceable rules):**

| Control | Default | Configurable |
|---|---|---|
| Execution timeout | 10s (beginner exercises) | Per-exercise override for approved heavier workloads (e.g. 60s for a model-training exercise) |
| CPU limit | 1 vCPU | Per-tier |
| Memory limit | 256MB (beginner) / 1GB (ML tier) | Per-tier |
| Max output size | 64KB truncated with notice | Config |
| Max uploaded file size (EDA lab) | 50MB synchronous; larger → async Celery pipeline | Config |
| Filesystem | Ephemeral, wiped on container destroy, no host mount | Fixed |
| Network | None (default-deny egress) | Allowlist only for explicitly-approved exercises (e.g. a lesson that legitimately calls a public API) |
| Process count | Capped (e.g. 32) | Fixed |
| Credentials exposed to sandbox | None — no host, cloud, or DB credentials ever injected | Fixed |
| Rate limiting | Per-user run quota (e.g. N runs/minute) via Redis token bucket | Config |
| Audit | Every run logged (`audit_logs`): user, exercise, timestamp, resource usage, exit code | Fixed |

**SQL Lab specifics:** each session gets its **own Postgres schema** (or a dedicated low-privilege role scoped via `SET search_path` + `REVOKE` on all other schemas) inside a database instance reserved for lab data — never the application's own transactional database. Query execution goes through a constrained proxy that enforces statement timeouts and blocks non-DDL/DML statement types the exercise doesn't need (e.g. no `COPY TO PROGRAM`, no superuser statements).

**Output streaming:** WebSocket connection between browser and Execution Gateway; the gateway relays stdout/stderr chunks from the sandbox as they're produced, and kills the container on timeout, disconnect, or explicit stop.

---

## 8. AI Tutor Architecture

**Model:** Claude API (current model family). **Not** a fine-tuned model at v1 — context assembly + system prompting + RAG.

**Modes** (from your spec): Explain, Hint, Debug, Quiz Me, Interview Me, Review My Code, Review My Analysis, Explain This Graph, Explain This Error, Give Me a Project, Create Practice Questions. Implemented as a fixed set of **system-prompt templates** selected by the frontend, not free-form mode invention.

**Context assembly (what the tutor is allowed to see per request):** current lesson/exercise id, the learner's current code buffer, latest execution output/error, dataset schema (if relevant), last N attempts, skill level, active career path, and — for RAG — the top-k retrieved curriculum passages via `pgvector` similarity search over `ai_embeddings`.

**Guardrail `[RECOMMENDATION]`, directly enforcing your Socratic-tutor requirement:** the "Hint"/"Debug" system prompts explicitly instruct the model to diagnose and ask guiding questions rather than emit a corrected solution; "Review My Code" is the only mode allowed to show corrected code, and only as a diff with explanation. This is a prompt-engineering + eval concern for Phase 9, flagged here as an architectural constraint (the API contract must carry "mode" as a required field so the backend — not the client — selects the system prompt, preventing prompt injection from swapping tutor behavior).

**Persistence:** `ai_sessions`/`ai_messages` store full conversation history per learner for continuity and for later analysis of where learners get stuck (feeds the adaptive-learning recommendations in §15).

---

## 9. Dataset Architecture

`datasets` (metadata: name, description, source, license, domain, difficulty, suggested skills/projects, **original source link — never fabricated**) + `dataset_versions` (immutable file references in S3/MinIO, with row/column counts computed at ingest). Upload path: files ≤50MB processed synchronously for the EDA lab preview; larger files are queued to a Celery worker that profiles the dataset (dtypes, missingness, summary stats, correlations, outlier flags) and writes results back for the UI to poll/subscribe to. Licensing/source fields are **required, not optional**, at ingest — no dataset can be published without them, enforced at the admin-upload API layer, per your instruction never to fabricate ownership or licensing.

---

## 10. Curriculum & Learning-Path Architecture

`learning_paths → courses → modules → lessons → topics`, each lesson carrying the fixed structure from §58 of your spec (objectives, explanation, visual, example, code, interactive exercise, practice, quiz, challenge, common mistakes, summary, key terms, further resources) as **structured JSON content blocks** referencing typed block components on the frontend (so a "code example" block, a "quiz" block, and an "interactive exercise" block are distinct, renderable, and independently testable) rather than one large markdown blob. `skills` is a normalized table that lessons/quizzes/projects tag, and that `user_progress` rolls up against — this is what powers "what am I weak at" on the dashboard (§61) without any separate analytics system.

---

## 11. Mac Setup Architecture

A `tools`/`install_guides` knowledge base (see §12) plus a stateless **wizard flow** (architecture detection → career → experience level → generated checklist) implemented entirely in the Core API + frontend — no separate service needed. Architecture detection: the frontend reads `navigator.userAgent`/`navigator.platform` as a *hint* only (client-provided data is never trusted for security decisions, only for personalizing content) and always gives the user an explicit Apple Silicon / Intel toggle to override. Per your instruction, installation commands are **not hardcoded as permanently correct** — each `install_guides` row carries a `last_verified` date and a `source_url`, and the admin content workflow (§17) is the mechanism for keeping them current; the platform does not auto-execute installation commands, it displays them for the user to run themselves.

---

## 12. Tool/Resource Architecture

`tools` table exactly matches your §57 schema (name, description, category, official URL, docs URL, Mac/Apple-Silicon/Intel support flags, install method, Homebrew command if applicable, verification command, common errors, alternatives, last verified date). `resources` (learning resource library, §28–29) stores title/provider/topic/level/free-or-paid/description/URL/last-verified, sourced only from real, verifiable URLs — the admin workflow is the only way new rows are added, never auto-generated by the AI tutor.

---

## 13. Authentication & Security Architecture

**Auth:** email+password (bcrypt/argon2 hashing) and OAuth2 (Google, GitHub) via Authlib; short-lived JWT access tokens + rotating refresh tokens (httpOnly, secure, SameSite cookies — not localStorage, to reduce XSS token theft risk); email verification and password reset via signed, expiring tokens. RBAC with `student` / `instructor` / `admin` roles enforced via FastAPI dependency injection on every route, not just at the UI layer.

**Platform security controls:** Pydantic input validation on every endpoint; parameterized queries only (SQLAlchemy ORM — no raw string interpolation into SQL, which also protects the app DB even though the SQL Lab's isolated schema is the one place raw SQL from users is deliberately allowed, and only against that isolated schema); rate limiting (Redis token bucket) on auth endpoints and execution endpoints specifically; CORS locked to the known frontend origin; CSRF protection on cookie-authenticated state-changing routes; file upload validation (type/size/content sniffing, never trusting the client-supplied extension); secrets via environment variables / a secrets manager, never committed or exposed to the frontend bundle; `audit_logs` for admin actions and code-execution events.

---

## 14. Search Architecture

`[RECOMMENDATION]` Start with **PostgreSQL full-text search** (`tsvector`/`tsquery` + GIN indexes) across curriculum, tools, datasets, projects, resources, and glossary — a materialized `search_index` view/table refreshed on content change. This avoids standing up Elasticsearch/Meilisearch before there's evidence it's needed (YAGNI, and it's one less service to secure and operate). Documented upgrade path: swap the query layer for Meilisearch/Typesense if relevance quality or query volume outgrow Postgres FTS — the API contract (`GET /search?q=&filters=`) doesn't change, only the implementation behind it.

---

## 15. Progress & Gamification Architecture

`user_progress` is the single source of truth every dashboard widget reads from (§62, §65 — no widget is allowed to show a number that isn't derived from real activity rows). XP, streaks, and badges are computed server-side from actual events (lesson completed, quiz passed, project submitted, lab exercise passed) written into an append-only activity log, not mutable counters — this makes the numbers auditable and prevents drift between "what happened" and "what the dashboard shows." Adaptive recommendations (§37) are a scheduled job that scans recent `quiz_attempts`/`code_submissions` failure patterns per skill and writes suggestions the dashboard reads — not a live ML model at v1, which would be premature given no training data yet exists.

---

## 16. Career Architecture

`career_paths` (Data Analyst, Data Scientist, Data Engineer, ML Engineer, Analytics Engineer, BI Analyst) each map to a weighted set of `skills`; a learner's progress against their selected path's skill set drives the "career progress" dashboard widget and the personalized Mac Setup Wizard checklist (§15 of your spec) — same skills taxonomy reused across curriculum, gamification, and career, rather than three separate systems.

---

## 17. Admin Architecture

Admin is **not a separate app** — it's a role-gated section of the same Core API + frontend (simpler to build and secure than a parallel admin service at this stage). Admins get CRUD over curriculum content, datasets, tools/resources/install-guides, career paths, users, certificates, and badges, all through the same validated Pydantic schemas as the public read paths (so admin-entered data can never bypass the same integrity constraints, e.g. a tool can't be saved without a real source URL).

---

## 18. Complete Folder Structure

```
DataForge/
  frontend/
    src/
      app/            # app shell, providers, router
      components/      # shared, design-system-level components
      features/
        auth/ dashboard/ courses/ lessons/ quizzes/ labs/
        datasets/ projects/ ai-tutor/ progress/ career/
        portfolio/ mac-setup/ resources/ glossary/ certificates/ admin/
      layouts/
      pages/
      routes/
      hooks/
      lib/
      services/        # typed API clients (TanStack Query hooks live here)
      stores/           # Zustand — kept small, see §4
      types/
      utils/
      styles/
      assets/
  backend/
    app/
      api/              # versioned routers, one per module
      core/             # config, db, security, logging, rate-limit
      models/
      schemas/
      services/         # business logic per module
      repositories/     # DB access per module
      workers/           # Celery tasks
      execution/         # client to the Execution Gateway — no execution logic here
      ai/                # tutor orchestration, RAG, prompt templates
      curriculum/
      datasets/
      analytics/
      utils/
    alembic/
    tests/
  execution-service/     # separate deployable — Execution Gateway + Sandbox Orchestrator
    gateway/
    orchestrator/
    sandbox-images/       # base images per lab type (python, sql, r)
  infra/
    docker-compose.yml
    docker-compose.prod.yml
    traefik/
    github-actions/
  docs/
    PHASE-1-ARCHITECTURE.md   # this file
```

---

## 19. API Architecture

REST, versioned (`/api/v1/...`), one router module per feature under `backend/app/api/`. Resource-oriented paths (`/api/v1/courses/{id}/lessons`), consistent envelope for pagination/errors, OpenAPI schema auto-generated by FastAPI and served as the "API Documentation" site page from §9 (no hand-maintained duplicate). Execution and AI-tutor streaming use WebSocket endpoints (`/ws/execution/{session_id}`, `/ws/ai-tutor/{session_id}`) rather than REST, since both are long-lived, chunked-output interactions.

---

## 20. WebSocket Architecture

Two legitimate uses, both already named above — **not** used for general data fetching (TanStack Query + REST covers that fine):
1. **Code execution output streaming** (Execution Gateway ↔ browser).
2. **AI tutor streaming responses** (Core API ↔ browser), so answers appear token-by-token like the Claude API's own streaming.

Both are authenticated on connect (JWT in the handshake), scoped to one session, and closed server-side on timeout/completion.

---

## 21. Background Job Architecture

Celery + Redis broker. Job categories: large-dataset profiling (EDA lab async path), certificate PDF generation, AI-tutor embedding generation/refresh for RAG, spaced-repetition schedule computation, transactional email (verification, password reset, notifications), scheduled adaptive-learning recommendation scans (§15). Each task is idempotent and retried with backoff; results/status pollable via a job-status endpoint the frontend subscribes to.

---

## 22. Storage Architecture

MinIO in development (S3-API-compatible, runs in Docker Compose), a real S3-compatible bucket in production. Buckets: `datasets`, `user-uploads`, `certificates`, `exports`. All access via signed URLs generated by the Core API — the frontend never holds bucket credentials.

---

## 23. Caching Architecture

Redis for: TanStack-Query-invalidation-friendly server-side response caching on expensive read endpoints (curriculum tree, tool/resource lists), rate-limit counters, Celery broker/result backend, and short-lived session/execution-session metadata (which sandbox is running for which user right now). Cache invalidation is explicit (write-through on content mutation), not TTL-only, for anything admin-edited.

---

## 24. Testing Strategy

| Layer | Tooling | Covers |
|---|---|---|
| Backend unit | pytest | Services, repositories, schema validation |
| Backend integration | pytest + testcontainers (real Postgres/Redis) | Auth flows, quiz scoring, progress writes, execution-gateway contract |
| Frontend unit | Vitest + React Testing Library | Components, hooks, stores |
| E2E | Playwright | Golden paths: signup → lesson → quiz → lab run → progress update |
| Load | k6, targeted at the Execution Gateway specifically | Confirms sandbox quotas/timeouts hold under concurrent runs — this is the one subsystem where a load failure is also a security failure |
| Security | Dependency scanning (GitHub Dependabot/CodeQL) + the sandbox escape checks folded into execution-service integration tests | — |

---

## 25. CI/CD Strategy

GitHub Actions: lint + type-check (ruff/mypy, eslint/tsc) → unit tests → integration tests → build Docker images (core-api, execution-gateway, sandbox base images, frontend) → push to registry → deploy. Execution-service images are built and scanned separately from the core API image, since they define the security boundary.

---

## 26. Deployment Strategy

`[RECOMMENDATION]` Start with Docker Compose on a single well-resourced host (or a small managed-container platform) behind Traefik, with managed Postgres and managed S3-compatible storage — not Kubernetes on day one. This matches the modular-monolith decision in §3: don't pay orchestration-platform tax before the traffic/team size justifies it. Documented upgrade path: the Execution Gateway/Orchestrator is the first candidate to move to a dedicated autoscaled node pool (e.g. Kubernetes with gVisor `RuntimeClass`) once concurrent lab usage requires horizontal scaling — its stateless-per-run design already makes that move additive, not a rewrite.

---

## 27. Development Roadmap (15 Phases)

1. Product & Technical Architecture *(this document)*
2. Database Schema & ERD
3. Backend API Foundations & Authentication
4. Frontend Foundations & Design System
5. Core Curriculum Data Models
6. Mac Setup Wizard & Tool Database
7. Interactive Code Execution Architecture (build-out of §7)
8. Python, SQL, R & Statistics Labs
9. AI Tutor
10. Projects & Dataset Explorer
11. Progress, Gamification & Spaced Repetition
12. Admin Dashboard
13. Testing & CI/CD
14. Security Hardening & Performance
15. Deployment

---

## 28. Risks & Mitigation

| Risk | Mitigation |
|---|---|
| Sandbox escape / resource exhaustion | gVisor isolation, hard quotas, network default-deny, dedicated load/security testing (§24), never share credentials into sandbox |
| Scope creep (this spec covers ~60 subsystems) | Strict phase gates with your explicit approval before each phase, as you've required |
| AI tutor giving away answers instead of teaching | Mode-locked system prompts enforced server-side, not client-selectable free text (§8) |
| Fabricated tool/dataset/resource info | Admin-only content entry with required source/license/last-verified fields, no AI-generated catalog rows (§9, §12) |
| Postgres FTS search quality plateauing | Documented, contract-stable upgrade path to Meilisearch/Typesense (§14) |
| Over-building infra before there are users | Docker Compose first, Kubernetes only for the execution tier and only when justified (§26) |

---

## 29. Scalability Considerations

Core API scales horizontally behind Traefik (stateless, JWT-based auth — no sticky sessions needed) with Postgres read replicas for read-heavy curriculum/dashboard traffic once needed. Execution is the one component expected to need independent scaling (bursty, resource-heavy) — its stateless-per-run orchestrator design (§7, §26) is what makes that possible without touching the rest of the system. Celery workers scale independently by queue (separate queues for "fast" jobs like email vs. "heavy" jobs like large-dataset profiling, so one doesn't starve the other).

---

## 30. UI/UX Architecture — Proposed Design System

`[RECOMMENDATION — original, since no design was supplied]` DataForge should feel like a **developer tool crossed with a data lab**, not a generic course-catalog SaaS: closer in spirit to how Linear, Vercel, and JupyterLab present dense, professional information, applied to a learning context.

**Color tokens** (dark-first, since labs/code/terminals dominate the experience):

| Token | Role |
|---|---|
| `--bg` | App background (near-black, not pure black) |
| `--surface` | Panel/sidebar background, one step up from `--bg` |
| `--card` | Card background, one step up from `--surface` |
| `--border` | Hairline borders between panels |
| `--text` | Primary text |
| `--text-muted` | Secondary/caption text |
| `--primary` | Brand indigo/violet — primary actions, active nav |
| `--accent` | Teal — used sparingly for data/success emphasis (charts, "run" success) |
| `--success` / `--warning` / `--error` / `--info` | Standard semantic states |

A light theme is derived from the same tokens (not a separate design) so both are maintainable from one source.

**Typography:** Inter (or system-ui fallback) for UI text; JetBrains Mono (or Menlo fallback) for code, terminal, SQL, and tabular data — this split is the single biggest signal that the product is a coding/data tool rather than a marketing site.

**Core components** (per your §66 checklist): persistent collapsible sidebar (course tree / lab nav), top bar with global command palette (`Cmd+K`) for search, cards (course/lesson/project/dataset — one card primitive, style variants), split-pane lab layout (editor left, output/visualization right — this is the signature interaction pattern across Python/SQL/Stats/Viz labs), Monaco-based code editor with a consistent run/stop/reset/save toolbar, xterm.js terminal panel, progress bars *and* progress rings (rings for dashboard skill mastery, bars for linear lesson/course completion), badges/toasts for gamification events, breadcrumbs for curriculum depth, tabs for lesson sub-sections (Explanation / Code / Exercise / Quiz).

**States required on every interactive component:** default, hover, active/pressed, focus-visible (keyboard), disabled, loading (skeleton, not spinner, for content; spinner only for actions), empty (with a clear next action, never a bare "no data"), error (with retry, not a dead end).

---

## 31. Design System → Functionality Mapping

| UI element | Backed by |
|---|---|
| Sidebar course tree | `learning_paths`/`courses`/`modules`/`lessons` |
| Progress rings/bars | `user_progress` |
| Command palette search | Search API (§14) |
| Lab split-pane run button | Execution Gateway WS session |
| AI tutor panel | `ai_sessions`/`ai_messages` + streaming WS |
| Dataset card → EDA lab | `datasets`/`dataset_versions` + profiling job status |
| Badge/toast on completion | Gamification event write → `achievements`/`badges` |
| Mac Setup Wizard checklist | `tools`/`install_guides` filtered by wizard answers |
| Career progress widget | `career_paths` + skill rollup from `user_progress` |

Every element in this table has a real data path — none of them is a static/fake number, per your §70 requirement.

---

## 32. Phase 2 Plan (Exact)

Phase 2 will deliver, and only:
1. Full PostgreSQL schema (all tables from §6, column-level) as SQL/SQLAlchemy models.
2. Complete ERD (described + generated diagram).
3. Alembic migration setup and first migration.
4. Explicit FK/index/constraint decisions with rationale per table group.
5. No API routes, no frontend, no execution logic yet.

Waiting for your approval before starting Phase 2.
