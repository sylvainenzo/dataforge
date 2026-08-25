# DataForge V2 — Audit Report

**Date:** 2026-08-25
**Scope:** Response to the "DataForge V2 — Extreme Completion" directive. This is a real audit against the live codebase and database, not a restatement of the original spec's ambitions.

## How to read this

Every claim below was checked, not assumed — either by reading the actual source file, or by querying the live `dataforge_dev` database, or by hitting the running API. Row counts are exact as of this audit. Where something is a judgment call rather than a fact, it's marked as such.

---

## 1. Current state, in one paragraph

DataForge is a working full-stack app (FastAPI + Postgres/Redis backend, React/Vite frontend, a separate execution-service for sandboxed code) with real authentication, real RBAC, a real (if small) curriculum with working quizzes and progress tracking, a real gamification system tied to actual activity, a real spaced-repetition flashcard system, a working SQL Lab and Python Lab, a working admin content-management UI, working account settings, and a working English/French language toggle. It is **not** a "Data Science university" in the sense the directive describes — it's an honest, small, working slice of one. The gap between what exists and what the directive asks for is not a bug list; it's mostly content volume and infrastructure this environment cannot provide (Firecracker/gVisor, Spark, Kafka, Airflow, cloud data warehouses).

## 2. What works (verified, not assumed)

| Feature | Status | Evidence |
|---|---|---|
| Auth (register/login/refresh/logout, RBAC) | **Working** | 60/60 backend tests pass; manually verified login/logout/role-guard flows |
| Admin content CRUD (courses/modules/lessons/quizzes) | **Working** | Full create/update/delete verified via curl and browser UI this session; regression-tested |
| Account settings (change password, display name) | **Working** | Verified end-to-end; old password confirmed rejected after change |
| Language toggle (English/French) | **Working, UI-chrome only** | Verified: persists across reload, switches instantly. Does **not** translate lesson/course content — that's a separate, much larger effort (see §4) |
| Curriculum (courses → modules → lessons → quizzes) | **Working, small** | 4 courses, 16 lessons, 5 quizzes — real, original content, not filler |
| Gamification | **Working, real** | Badges/XP/streaks computed live from actual completed lessons/quizzes, never a stored counter that could drift |
| Spaced repetition (flashcards) | **Working, real** | Real SM-2 implementation; 22 flashcards; now has full API test coverage (added this session, previously only the algorithm was tested) |
| SQL Lab | **Working, small** | Real query validation against an isolated read-only Postgres role; 5 hand-authored exercises |
| Python Lab | **Working, minimal** | Real subprocess execution with resource limits; one free-form editor, no structured exercise set |
| R Lab | **Just built, working** | R is installed on this machine (`/usr/local/bin/Rscript`, R 4.5.3) — built real R code execution this session, not a stub. Found and fixed a real bug in the process: the process-count resource limit (`RLIMIT_NPROC`) was hardcoded to 16, which is a *system-wide* per-user limit, not a per-subprocess one — on any machine already running more than 16 processes (every real dev machine, always) this silently broke any language needing an internal fork, which R does on startup and Python's single-process scripts happen not to. Fixed to budget headroom above current usage instead of a fixed low number. Frontend page written; **not yet wired into the router/Labs index** — next step. |
| Resources & Glossary | **Working** | 8 real, individually-verified resource links (fetched and confirmed live, not recalled) + 10 glossary terms tied to actual taught content |
| Career paths | **Working, real** | 6 paths with honest skill weightings against the 5 skills that actually exist; progress computed live from completed lessons (proved this by completing a lesson mid-session and watching the number move) |
| Search | **Working, real** | Real Postgres full-text search across courses/lessons/tools/projects/resources/glossary; was previously a cosmetic input explicitly labeled as fake in the code |
| AI Tutor | **Code-complete, needs a key** | Real WebSocket integration, graceful 503 when unconfigured — genuinely done, just needs an `ANTHROPIC_API_KEY` the user provides (not something to fabricate or reuse Claude Code's own credentials for) |
| Mac Setup Wizard | **Working** | Real 4-step flow (architecture detect → career → experience → checklist), 8 tools with full install guides |

## 3. What's broken, superficial, or missing

| Area | Status | Detail |
|---|---|---|
| Statistics Lab, Math Lab | **Missing** | Disabled "Coming later" cards. No design decision made yet on whether these are code-execution labs or interactive-simulation/practice-problem formats (the directive wants sliders/live simulations — that's a real, scoped frontend build, not infrastructure) |
| Data Visualization Lab, ML Lab, DL Lab, Data Engineering Lab, Spark/Airflow/Kafka/dbt labs | **Missing** | Not started. Several of these (Spark, Kafka, Airflow, dbt) require installing and running real infrastructure this dev machine doesn't have and that I should not silently install without your go-ahead given the footprint (Airflow alone pulls in a scheduler + metadata DB) |
| Excel, Power BI, Tableau courses | **Missing** | Not started. Flagging now: **Power BI Desktop does not run natively on macOS** — the directive itself asks me to be accurate about this rather than claim otherwise, and I will be when I write that course |
| Course volume | **Far below target** | 4 courses / 16 lessons vs. the directive's "hundreds of lessons" across dozens of subject schools. This is the single biggest gap — closing it is content-authoring work, measured in many more sessions, not a bug |
| Projects | **Minimal** | 2 real project briefs (with full rubrics), zero submission/review flow. Directive wants 100+ projects across 4 tiers — not attempted |
| Datasets | **Minimal** | 1 dataset seeded |
| Certificates | ✅ **Done** | Issuing (completion-gated), real PDF generation, public verification, download — verified end-to-end live |
| Portfolio builder | ✅ **Done** | Public opt-in page at `/portfolio/{user_id}`, real passed-project + certificate data, bio + visibility toggle in Settings |
| Interview question bank | ✅ **Done** | 30 real questions, browsable/filterable, admin CRUD |
| Industry specializations (finance/healthcare/retail/etc.) | **Missing** | Not started — flagged P3, needs a scoping conversation |
| Skill graph / adaptive recommendations ("you keep failing JOINs, here's the lab") | **Missing** | Gamification reads real activity, but nothing yet *acts* on weak-skill detection |
| Notifications | **Missing** | Table exists in the schema, zero application logic anywhere |
| Admin CRUD for resources/tools/career paths/datasets | **Missing** | Course/module/lesson/quiz CRUD is done; the rest of the content types still require direct seed scripts |
| gVisor/Firecracker sandbox | **Documented gap, not fixable here** | Code execution runs as a resource-limited OS subprocess, honestly labeled as dev-only in the code and the UI ("Dev sandbox" badge). Real container isolation needs infrastructure (Docker + gVisor runtime) this environment doesn't have |
| Test coverage on older features | **Partial** | New features (career, resources, search, flashcards, admin CRUD, account settings) all have real integration tests added this session. Projects, datasets, and AI tutor still have no test files |

## 4. On "translate everything" vs. "translate the UI"

The French toggle translates navigation, buttons, forms, and page chrome. It does not translate the ~16 lessons' worth of English teaching content, because that's not a UI-string swap — it's translating real technical educational writing accurately, which is its own large content project (and doing it badly, e.g. with unreviewed machine translation of technical terms, would actively hurt a French-speaking learner). If full French curriculum content is wanted, that's worth scoping as its own phase rather than folding into "add a language switcher."

## 5. Honest infeasibility notes

A few directive items I want to flag now rather than silently skip or half-fake later:

- **Firecracker/gVisor**: genuinely requires a Linux host with the gVisor runtime or a Firecracker-capable hypervisor. Not installable as a side effect of writing code on this Mac.
- **Spark/Kafka/Airflow/dbt labs**: each is real infrastructure (a scheduler + metadata store, a broker, a distributed runtime). I can teach the *concepts* and even guided, config-only exercises without running the real services, but a "real Spark cluster in a lab" isn't happening on a laptop dev environment without a much bigger conversation about footprint first.
- **Power BI on macOS**: does not exist natively. I'll teach it honestly (web version, Mac limitations, alternatives) rather than write install instructions for something that isn't there.
- **Cloud data warehouses (Snowflake/BigQuery/Redshift/Databricks)**: teaching them conceptually is reasonable; provisioning real accounts is not something I should do without you providing credentials and explicitly asking for it.

None of this means "don't build toward the vision" — it means the roadmap below sequences the achievable parts first and calls out the parts that need an explicit decision from you before I sink time into them.

---

# DataForge V2 — Master Roadmap

Priorities: **P0** critical/broken · **P1** high-value, achievable soon · **P2** important, larger effort · **P3** enhancement / needs a scoping decision first.

### P0 — Finish what's mid-flight
- Wire the already-built R Lab into the router and Labs index (it's built and tested, just not linked in yet)
- Add admin CRUD for the content types still seed-script-only (resources, tools, career paths)

### P1 — High-value, realistically achievable in the next few sessions
- Statistics Lab as an interactive-simulation format (sliders for sample size/effect size, live-updating distribution charts) — genuinely different from "another code editor," matches the directive's own description, no new infrastructure needed
- Expand each existing subject (Python, SQL, Statistics, pandas) with intermediate/advanced tier courses — the `LearningLevel` enum already supports 5 tiers (beginner/practical/technical/advanced/professional), just needs content
- Data Visualization course + a real Data Viz Lab (matplotlib/seaborn via the existing Python execution path — no new infra, just new lesson/lab content)
- A basic skill-graph-driven recommendation ("you're weak here, try this") on the dashboard, since the underlying per-skill progress data already exists (built for career paths this session)
- Expand the dataset and resource libraries with more individually-verified entries

### P2 — Important, bigger lifts
- ✅ Project submission flow (upload + review), and grow the project library
- ✅ Certificates (issuing logic + simple PDF generation) — verified end-to-end in the live browser: issue, real PDF download, public verification
- ✅ Interview question bank — 30 real questions across SQL/Python/Statistics/Pandas/Behavioral/Case Study, filterable by category/difficulty/career path, admin CRUD, verified live in the browser
- ✅ Portfolio builder — opt-in public page at `/portfolio/{user_id}` showing real passed project submissions and issued certificates, bio + public/private toggle in Settings, verified end-to-end live (private-by-default, public view, 404 when private)
- ✅ Admin CRUD for the remaining content types (projects, datasets)
- ✅ Broader test coverage — datasets (public list/detail, real CSV upload + profiling, format/size/rate-limit rejection) and AI Tutor (session/message CRUD, WebSocket auth/ownership gating) now have test files; 112/112 backend tests passing

### P2 — complete
Every item on this list is now implemented, tested, and verified live in the browser.

### P3 — Needs a scoping conversation before starting
- Spark/Kafka/Airflow/dbt labs (real infra footprint — what's actually OK to install here?)
- Excel/Power BI/Tableau courses (teachable conceptually now; Power BI's Mac limitation needs to be represented honestly)
- Industry specialization tracks (finance/healthcare/retail/etc.) — valuable, but this is dozens more courses on top of the core ones
- Full French translation of curriculum *content* (not just UI) — separate effort from the language switcher
- gVisor/Firecracker production sandbox — needs a decision on target deployment infra, not something to attempt against this dev machine

---

## What I'll do next

Starting with P0 (finish the R Lab wiring), then moving into P1 in the order above, checkpointing with real verification (tests + browser checks) after each piece rather than batching silently — same pattern as the rest of this session. Flagging again: I won't install Spark/Kafka/Airflow/dbt or provision cloud accounts without you explicitly signing off on that, given the footprint and credentials involved.
