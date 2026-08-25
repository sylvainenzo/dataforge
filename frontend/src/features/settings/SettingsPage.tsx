import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Briefcase, Check, Copy, Globe, KeyRound, UserRound } from 'lucide-react'
import { type FormEvent, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { AUTH_QUERY_KEY, useCurrentUser } from '@/hooks/useAuth'
import { ApiError } from '@/lib/api'
import { authApi } from '@/services/authApi'
import { portfolioApi } from '@/services/portfolioApi'
import { useUiStore, type Language } from '@/stores/uiStore'

function ProfileSection() {
  const { user } = useCurrentUser()
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [displayName, setDisplayName] = useState(user?.display_name ?? '')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSaved(false)
    setIsSaving(true)
    try {
      const updated = await authApi.updateProfile(displayName)
      queryClient.setQueryData(AUTH_QUERY_KEY, updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.profile')}</CardTitle>
        <UserRound className="h-4 w-4 text-text-muted" />
      </CardHeader>
      <p className="mb-4 text-sm text-text-muted">{t('settings.profileDescription')}</p>
      <form onSubmit={onSubmit} className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1">
          <Input
            label={t('settings.displayName')}
            name="display_name"
            required
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={isSaving}>
          {saved ? (
            <>
              <Check className="h-4 w-4" /> {t('settings.saved')}
            </>
          ) : (
            t('settings.save')
          )}
        </Button>
      </form>
      {error && <p className="mt-2 text-sm text-error">{error}</p>}
    </Card>
  )
}

function PasswordSection() {
  const { t } = useTranslation()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSaved(false)
    setIsSaving(true)
    try {
      await authApi.changePassword(currentPassword, newPassword)
      setCurrentPassword('')
      setNewPassword('')
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.password')}</CardTitle>
        <KeyRound className="h-4 w-4 text-text-muted" />
      </CardHeader>
      <p className="mb-4 text-sm text-text-muted">{t('settings.passwordDescription')}</p>
      <form onSubmit={onSubmit} className="flex flex-col gap-3">
        <Input
          label={t('settings.currentPassword')}
          type="password"
          name="current_password"
          autoComplete="current-password"
          required
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
        />
        <Input
          label={t('settings.newPassword')}
          type="password"
          name="new_password"
          autoComplete="new-password"
          required
          minLength={8}
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
        />
        {error && <p className="text-sm text-error">{error}</p>}
        <Button type="submit" disabled={isSaving} className="self-start">
          {saved ? (
            <>
              <Check className="h-4 w-4" /> {t('settings.passwordChanged')}
            </>
          ) : (
            t('settings.changePassword')
          )}
        </Button>
      </form>
    </Card>
  )
}

function PortfolioSection() {
  const { user } = useCurrentUser()
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const { data: settings, isLoading } = useQuery({ queryKey: ['portfolio', 'settings'], queryFn: portfolioApi.settings })
  const [bio, setBio] = useState('')
  const [portfolioPublic, setPortfolioPublic] = useState(false)
  const [saved, setSaved] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (settings) {
      setBio(settings.bio ?? '')
      setPortfolioPublic(settings.portfolio_public)
    }
  }, [settings])

  const saveMutation = useMutation({
    mutationFn: () => portfolioApi.updateSettings({ bio, portfolio_public: portfolioPublic }),
    onSuccess: (updated) => {
      queryClient.setQueryData(['portfolio', 'settings'], updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    },
  })

  const publicUrl = user ? `${window.location.origin}/portfolio/${user.id}` : ''

  function copyLink() {
    navigator.clipboard.writeText(publicUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (isLoading) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.portfolio')}</CardTitle>
        <Briefcase className="h-4 w-4 text-text-muted" />
      </CardHeader>
      <p className="mb-4 text-sm text-text-muted">{t('settings.portfolioDescription')}</p>
      <div className="flex flex-col gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-text">{t('settings.bio')}</label>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            rows={3}
            className="w-full rounded-lg border border-border bg-surface p-2 text-sm text-text"
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-text">
          <input
            type="checkbox"
            checked={portfolioPublic}
            onChange={(e) => setPortfolioPublic(e.target.checked)}
          />
          {t('settings.portfolioPublic')}
        </label>
        {portfolioPublic && (
          <div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-2 text-xs">
            <span className="flex-1 truncate text-text-muted">{publicUrl}</span>
            <button onClick={copyLink} className="flex items-center gap-1 text-primary hover:underline">
              <Copy className="h-3 w-3" /> {copied ? t('settings.copied') : t('settings.copyLink')}
            </button>
          </div>
        )}
        <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending} className="self-start">
          {saved ? (
            <>
              <Check className="h-4 w-4" /> {t('settings.saved')}
            </>
          ) : (
            t('settings.save')
          )}
        </Button>
      </div>
    </Card>
  )
}

function LanguageSection() {
  const { t } = useTranslation()
  const language = useUiStore((s) => s.language)
  const setLanguage = useUiStore((s) => s.setLanguage)

  const options: { value: Language; label: string }[] = [
    { value: 'en', label: t('settings.english') },
    { value: 'fr', label: t('settings.french') },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('settings.language')}</CardTitle>
        <Globe className="h-4 w-4 text-text-muted" />
      </CardHeader>
      <p className="mb-4 text-sm text-text-muted">{t('settings.languageDescription')}</p>
      <div className="flex gap-2">
        {options.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setLanguage(opt.value)}
            className={`rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${
              language === opt.value
                ? 'border-primary bg-primary-soft text-primary'
                : 'border-border text-text-muted hover:bg-surface'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </Card>
  )
}

export function SettingsPage() {
  const { t } = useTranslation()

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <h1 className="text-xl font-bold text-text">{t('settings.title')}</h1>
      <ProfileSection />
      <PortfolioSection />
      <PasswordSection />
      <LanguageSection />
    </div>
  )
}
