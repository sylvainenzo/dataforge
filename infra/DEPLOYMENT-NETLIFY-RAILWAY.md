# Deploying DataForge — Netlify (frontend) + Railway (backend)

This is the actual path being used to get a first version of DataForge
live, as an alternative to the Traefik/VPS architecture in
`DEPLOYMENT.md`. It trades some control for far less setup: no server to
manage, no Docker knowledge needed on your end, HTTPS handled
automatically by both platforms.

**Scope of this first deploy:** frontend + core API + Postgres + Redis.
The separate `execution-service` (real Python/R code execution) is
**not** deployed yet — the Python/R/Data Viz labs are gated off
(`VITE_CODE_LABS_ENABLED=false`) because that service isn't safe to expose
publicly without a real sandbox (gVisor/Firecracker) in front of it. SQL
Lab and Statistics Lab are unaffected and work normally.

## 0. Prerequisites (accounts only you can create)

- A GitHub account, with this repo pushed to it (private repo recommended)
- A [Railway](https://railway.app) account
- A [Netlify](https://netlify.com) account
- Optionally, a domain name — not required to get a working URL

## 1. Push the code to GitHub

1. Create a new **private** repository on GitHub (don't initialize it with
   a README — this repo already has one).
2. From the `DataForge` folder:
   ```bash
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```

## 2. Railway — Postgres, Redis, and the backend API

1. New Project → **Provision PostgreSQL** (adds a managed Postgres and
   sets `DATABASE_URL` on it automatically — you'll copy that value over
   to the API service in step 4).
2. In the same project → **New → Database → Add Redis**.
3. **New → GitHub Repo** → select this repo. When Railway asks for the
   root directory / service source, set it to `backend` — this is a
   monorepo, and Railway needs to know which subfolder to build. It will
   detect `backend/Dockerfile` and build from that automatically.
4. On the new API service, open **Variables** and set:

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | Reference the Postgres plugin's `DATABASE_URL` variable (Railway lets you reference another service's variable directly — use that, don't hand-copy it) |
   | `REDIS_URL` | Reference the Redis plugin's `REDIS_URL` variable, same way |
   | `SQL_LAB_DATABASE_URL` | Placeholder for now — set to the same value as `DATABASE_URL` just so the app boots. **Do not leave it that way**: step 7 below runs a script that creates a real isolated database + read-only role and prints the correct value to paste in here, then redeploy. |
   | `JWT_SECRET` | Generate one: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` — a fresh value, never the dev one |
   | `SESSION_SECRET` | Generate the same way, a **different** fresh value |
   | `COOKIE_SECURE` | `true` |
   | `COOKIE_SAMESITE` | `none` (required — frontend and backend are on different domains) |
   | `CORS_ORIGINS` | `["https://<your-site-name>.netlify.app"]` — you'll get the exact Netlify URL in step 3 below; come back and set this after |

   You do *not* need to set `PORT` — Railway injects it automatically and
   the Dockerfile now respects it.

5. Deploy. Railway will build the image, run `alembic upgrade head`, and
   start the API (see the updated `backend/Dockerfile` — migrations now
   run automatically on every boot).
6. Once it's up, open the service's **Settings → Networking** and generate
   a public domain. That URL (e.g. `https://dataforge-api-production.up.railway.app`)
   is your backend's public address — you'll need it in step 3.
7. **Seed real content** — an empty database has zero courses. Use
   Railway's **Shell** (in the service view) to run, in order:
   ```bash
   python3 scripts/seed_curriculum.py
   python3 scripts/seed_curriculum_intermediate.py
   python3 scripts/seed_curriculum_dataviz.py
   python3 scripts/seed_curriculum_stats_wrangling.py
   python3 scripts/seed_resources.py
   python3 scripts/seed_tools.py
   python3 scripts/seed_career_paths.py
   python3 scripts/seed_projects.py
   python3 scripts/seed_datasets.py
   python3 scripts/seed_gamification.py
   python3 scripts/seed_interview_questions.py
   ```
   All are idempotent — safe to re-run if one fails partway through.
8. **Set up the SQL Lab's isolated sandbox.** Its sample data and
   read-only role were only ever created manually with psql on the
   original dev machine — this script reproduces that properly:
   ```bash
   python3 scripts/setup_sql_lab_sandbox.py
   ```
   It prints a `SQL_LAB_DATABASE_URL` at the end. Copy that into the
   service's Variables (replacing the placeholder from step 4) and
   redeploy. Without this, SQL Lab exercises will error — the tables it
   queries don't exist in the main database.
9. **Make yourself admin.** Sign up for a real account on the live site
   first (through the frontend, once step 3 is done), then from the same
   Railway shell:
   ```bash
   python3 scripts/grant_admin.py you@example.com
   ```
   There's no other way to create the first admin — the admin UI is
   itself admin-gated.

## 3. Netlify — the frontend

`netlify.toml` at the repo root already tells Netlify to build from
`frontend/`, run `npm run build`, and publish `dist/` — connecting the
repo should need no manual config.

1. Add new site → Import from GitHub → select this repo. Build settings
   should auto-fill from `netlify.toml`; confirm and deploy.
2. Before or after the first deploy, go to **Site configuration →
   Environment variables** and set:

   | Variable | Value |
   |---|---|
   | `VITE_API_BASE_URL` | The Railway backend URL from step 2.6, e.g. `https://dataforge-api-production.up.railway.app` |
   | `VITE_CODE_LABS_ENABLED` | `false` |

3. Trigger a redeploy if you set the env vars after the first build (env
   vars are baked in at build time, not read at runtime).
4. Note the resulting `https://<something>.netlify.app` URL — go back to
   Railway and set `CORS_ORIGINS` to include it exactly (step 2.4), then
   redeploy the backend so the new origin is allowed.

## 4. Verify

- Visit the Netlify URL, register a real account, confirm login works
  (this is the step that proves the cross-origin cookie settings are
  correct — if it silently fails to keep you logged in, `COOKIE_SAMESITE`
  or `CORS_ORIGINS` is the first thing to check).
- Browse to Courses — should show real seeded content, not an empty page.
- Confirm SQL Lab and Statistics Lab work; confirm Python/R/Data Viz labs
  show the "sandbox hardening" disabled state instead of trying to run
  code.
- Grant yourself admin (step 2.9) and confirm `/admin` loads.

## Known gaps at this launch state

- **No real code execution.** Intentional — see the scope note above.
- **Dataset/certificate uploads use local container storage, which
  Railway wipes on every redeploy.** Fine for the seeded datasets (they're
  re-seeded on shell access if lost), but any user-uploaded dataset or
  generated certificate PDF will disappear the next time the backend
  redeploys. Attach a Railway volume mounted at `/app/storage` as the
  minimum fix, or move to real object storage (S3/R2) for anything durable.
- **AI Tutor** stays disabled (503) until `ANTHROPIC_API_KEY` is set on
  the Railway service — add it as another variable in step 2.4 whenever
  you want it live; it's your key, so it's your call in your own time.
- **No email sending** — password reset / verification flows, if
  triggered, won't actually deliver anything without a transactional
  email provider wired in.
