import { type FormEvent, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { ApiError } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { authApi } from '@/services/authApi'

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { t } = useTranslation()

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await authApi.forgotPassword(email)
      setSent(true)
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        setError(err.message)
      } else {
        setError('Something went wrong. Try again.')
      }
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
          <h1 className="text-lg font-bold text-text">{t('auth.forgotPasswordTitle')}</h1>
          <p className="text-center text-sm text-text-muted">{t('auth.forgotPasswordDescription')}</p>
        </div>

        {sent ? (
          <div className="rounded-xl border border-success/30 bg-success-soft p-4 text-center text-sm text-text">
            {t('auth.resetLinkSent')}
          </div>
        ) : (
          <form onSubmit={onSubmit} className="flex flex-col gap-4 rounded-xl border border-border bg-card p-6 shadow-card">
            <Input
              label={t('auth.email')}
              type="email"
              name="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            {error && <p className="text-sm text-error">{error}</p>}
            <Button type="submit" disabled={isSubmitting} className="mt-1">
              {t('auth.sendResetLink')}
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
