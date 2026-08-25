import { type FormEvent, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useRegister } from '@/hooks/useAuth'

export function RegisterPage() {
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const register = useRegister()
  const navigate = useNavigate()
  const { t } = useTranslation()

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setFormError(null)
    try {
      await register.mutateAsync({ email, password, display_name: displayName })
      navigate('/')
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Something went wrong. Try again.')
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
          <h1 className="text-lg font-bold text-text">{t('auth.createAccount')}</h1>
          <p className="text-sm text-text-muted">{t('auth.tagline')}</p>
        </div>

        <form onSubmit={onSubmit} className="flex flex-col gap-4 rounded-xl border border-border bg-card p-6 shadow-card">
          <Input
            label={t('auth.displayName')}
            name="display_name"
            autoComplete="name"
            required
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
          <Input
            label={t('auth.email')}
            type="email"
            name="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            label={t('auth.password')}
            type="password"
            name="password"
            autoComplete="new-password"
            minLength={8}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {formError && <p className="text-sm text-error">{formError}</p>}
          <Button type="submit" disabled={register.isPending} className="mt-1">
            {t('auth.createAccount')}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-text-muted">
          {t('auth.haveAccount')}{' '}
          <Link to="/login" className="font-medium text-primary hover:underline">
            {t('auth.signIn')}
          </Link>
        </p>
      </div>
    </div>
  )
}
