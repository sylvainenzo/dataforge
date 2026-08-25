import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useCurrentUser } from '@/hooks/useAuth'

/** Client-side gating for UX only — the real enforcement is server-side
 * (require_role() on every admin endpoint, verified with real 403s in
 * Phase 12 testing). This just avoids showing a broken, error-riddled page
 * to a user who will get 403s on every request anyway. */
export function RequireRole({ role, children }: { role: string; children: ReactNode }) {
  const { user, isLoading } = useCurrentUser()

  if (isLoading) {
    return <div className="flex h-full items-center justify-center text-sm text-text-muted">Loading…</div>
  }
  if (!user?.roles.includes(role)) {
    return <Navigate to="/" replace />
  }
  return <>{children}</>
}
