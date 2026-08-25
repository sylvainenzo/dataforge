# Written for Phase 15 but NOT built or run — no Docker in this environment.

FROM node:22-slim AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# VITE_API_BASE_URL/VITE_EXECUTION_WS_URL etc. must be real values at build
# time — Vite inlines them into the bundle, they cannot be swapped at
# container-start like a server-rendered app's env vars can.
RUN npm run build

FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
