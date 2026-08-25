import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError, api } from './api'

describe('api client', () => {
  const originalFetch = globalThis.fetch

  beforeEach(() => {
    globalThis.fetch = vi.fn()
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
    vi.restoreAllMocks()
  })

  it('sends credentials and a JSON content-type on every request', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response(JSON.stringify({ ok: true }), { status: 200 }))

    await api.get('/api/v1/health')

    const [, init] = vi.mocked(fetch).mock.calls[0]
    expect(init?.credentials).toBe('include')
    expect((init?.headers as Record<string, string>)['Content-Type']).toBe('application/json')
  })

  it('throws ApiError with the server-provided detail on a non-2xx response', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'Incorrect email or password' }), { status: 401 }),
    )

    await expect(api.get('/api/v1/auth/me')).rejects.toMatchObject({
      status: 401,
      message: 'Incorrect email or password',
    })
  })

  it('resolves undefined on a 204 No Content response', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response(null, { status: 204 }))

    await expect(api.post('/api/v1/lessons/x/complete')).resolves.toBeUndefined()
  })

  it('ApiError carries the HTTP status code', () => {
    const err = new ApiError(429, 'Too many requests')
    expect(err.status).toBe(429)
    expect(err.message).toBe('Too many requests')
    expect(err).toBeInstanceOf(Error)
  })
})
