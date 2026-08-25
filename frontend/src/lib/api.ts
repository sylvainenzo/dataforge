const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const REFRESH_PATH = '/api/v1/auth/refresh'
const NO_REFRESH_RETRY_PATHS = new Set([REFRESH_PATH, '/api/v1/auth/login'])

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// The access-token cookie expires after 15 minutes; the refresh-token
// cookie lasts 30 days. Without this, every session would silently end
// after 15 minutes regardless of how recently the person was active — the
// backend's /auth/refresh endpoint existed but nothing ever called it.
// Concurrent 401s (e.g. a page firing several requests on mount) share one
// in-flight refresh instead of each triggering their own.
let refreshPromise: Promise<boolean> | null = null

function refreshSession(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_BASE_URL}${REFRESH_PATH}`, { method: 'POST', credentials: 'include' })
      .then((res) => res.ok)
      .catch(() => false)
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

function rawRequest(path: string, init?: RequestInit): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: 'include', // send/receive the httpOnly auth cookies
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response = await rawRequest(path, init)

  if (response.status === 401 && !NO_REFRESH_RETRY_PATHS.has(path)) {
    if (await refreshSession()) {
      response = await rawRequest(path, init)
    }
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }))
    throw new ApiError(response.status, body.detail ?? 'Request failed')
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
}
