# DataForge Frontend — Phase 4 (Foundations + Design System)

React 18 + TypeScript + Vite + Tailwind CSS v4. See
`../docs/PHASE-1-ARCHITECTURE.md` for the phase roadmap.

## Setup

```bash
cd frontend
npm install
npm run dev   # http://localhost:5180 — matches the backend's CORS_ORIGINS
```

Requires the Phase 3 backend running at `http://localhost:8000` (see
`../backend/README.md`) — auth pages call it directly.

## What's real

- Full design system: color/typography tokens (dark-first, light derived
  from the same tokens), Button/Card/Badge/Input/ProgressBar/ProgressRing/
  EmptyState/Skeleton primitives, sidebar + topbar app shell, Cmd+K command
  palette shell.
- Real auth: register/login/logout call the actual backend API over
  cookies; `RequireAuth` genuinely redirects unauthenticated visits to
  `/login`; the dashboard shows the real signed-in user and role, not mock
  data.
- Every other nav destination (Courses, Labs, Projects, Datasets, etc.) is
  an honest "coming in Phase N" empty state — not a fake dashboard with
  invented numbers.

## Verified, not just written

Exercised in a real browser against the real Phase 3 API: registered a new
account through the UI, landed on the dashboard with the real email/role
shown, toggled dark/light theme, opened the command palette, navigated a
placeholder route, logged out, and confirmed the router redirects back to
`/login` when re-visiting a protected route with no session.

## Known gaps

- Mobile layout hasn't had a dedicated interaction pass yet (Phase 1 §63
  calls for an intentional mobile layout, not just a shrunk desktop one) —
  visually responsive at a glance, but not click-tested end-to-end on a
  mobile viewport in this phase.
- The command palette is UI-only; it says so. Real search needs the
  Postgres full-text search API from a later phase.
