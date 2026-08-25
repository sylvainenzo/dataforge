# Deployment — Phase 15

**Status: written, not deployed.** Everything below was authored to the
architecture in `docs/PHASE-1-ARCHITECTURE.md` §26 and follows current
Docker/Traefik best practice, but this development environment has no
Docker installed (confirmed absent back in Phase 7) — none of it has been
built or run. Verify a real `docker build` and `docker compose config`
before trusting it in production.

## What exists

- `backend/Dockerfile`, `execution-service/Dockerfile`, `frontend/Dockerfile`
  — multi-stage builds, non-root users, slim base images.
- `frontend/nginx.conf` — SPA fallback routing + long-term asset caching.
- `infra/docker-compose.yml` — local dev only (Postgres + Redis).
- `infra/docker-compose.prod.yml` — application tier for production
  (Traefik + core-api + execution-gateway + frontend), deliberately
  *without* Postgres/Redis containers — Phase 1 §26 recommends managed
  database/cache services in production, not stateful containers you
  operate yourself.
- `.github/workflows/ci.yml` — lint + test + build on every push (Phase 13).

## Before this goes anywhere real

1. **gVisor for the execution service.** This is the one non-negotiable
   item. `execution-service/app/orchestrator.py`'s `LocalSubprocessOrchestrator`
   is explicitly documented as dev-only — it must not run real untrusted
   users' code without the gVisor container runtime (`runtime: runsc` in
   the compose file, or a Kubernetes `RuntimeClass`) actually installed and
   enabled on the host. Nothing in this repo enforces that at deploy time;
   it is a deployment prerequisite, not a code guarantee.
2. **Managed Postgres + Redis**, not the dev compose file's containers.
3. **Real secrets** for `JWT_SECRET`, `SESSION_SECRET`, and (if used)
   `ANTHROPIC_API_KEY`/OAuth credentials — generate fresh values, never
   reuse the dev `.env` files.
4. **`COOKIE_SECURE=true`** once serving over HTTPS (Traefik terminates TLS
   in the compose file above) — cookies are only marked `Secure` when this
   is set, and it defaults to `false` for local HTTP development.
5. **DNS** for `APP_DOMAIN`, `API_DOMAIN`, `EXECUTION_DOMAIN` pointed at the
   host, and `ACME_EMAIL` set for Let's Encrypt.
6. An actual `docker compose -f docker-compose.prod.yml config` and build,
   verified on a machine that has Docker — this environment doesn't.

## What's out of scope here

Kubernetes manifests, a CDN in front of the frontend, database backup/
restore automation, and secrets-manager integration (Vault, AWS Secrets
Manager, etc.) are all reasonable next steps but weren't built — adding
them without a concrete hosting target to design against would be
speculative rather than real.
