import { type FormEvent, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { ApiError } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { authApi } from '@/services/authApi'

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const navigate = useNavigate()
  const { t } = useTranslation()

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await authApi.resetPassword(token, newPassword)
      navigate('/login', { state: { resetSuccess: true } })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-bg px-4">
      <div className="pointer-events-none absolute -left-24 -top-24 h-96 w-96 rounded-full bg-primary opacity-[0.15] blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 -right-24 h-96 w-96 rounded-full bg-spark opacity-[0.12] blur-3xl" />
      <div className="relative w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-forge font-mono text-sm font-bold text-white shadow-glow">
            DF
          </div>
          <h1 className="text-lg font-bold text-text">{t('auth.resetPasswordTitle')}</h1>
        </div>

        {!token ? (
          <div className="rounded-xl border border-error/30 bg-error-soft p-4 text-center text-sm text-error">
            {t('auth.invalidResetLink')}
          </div>
        ) : (
          <form onSubmit={onSubmit} className="flex flex-col gap-4 rounded-xl border border-border bg-card p-6 shadow-card">
            <Input
              label={t('auth.newPassword')}
              type="password"
              name="new_password"
              autoComplete="new-password"
              minLength={8}
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
            {error && <p className="text-sm text-error">{error}</p>}
            <Button type="submit" disabled={isSubmitting} className="mt-1">
              {t('auth.resetPassword')}
            </Button>
          </form>
        )}

        <p className="mt-4 text-center text-sm text-text-muted">
          <Link to="/login" className="font-medium text-primary hover:underline">
            {t('auth.backToSignIn')}
          </Link>
        </p>
      </div>
    </div>
  )
}
