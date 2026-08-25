import { LogOut, Menu, Moon, Search, Settings, Sparkles, Sun } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { useLogout } from '@/hooks/useAuth'
import { useUiStore } from '@/stores/uiStore'
import type { User } from '@/types/auth'

export function Topbar({ user }: { user: User | null }) {
  const toggleSidebar = useUiStore((s) => s.toggleSidebar)
  const theme = useUiStore((s) => s.theme)
  const toggleTheme = useUiStore((s) => s.toggleTheme)
  const setCommandPaletteOpen = useUiStore((s) => s.setCommandPaletteOpen)
  const setAiTutorOpen = useUiStore((s) => s.setAiTutorOpen)
  const logout = useLogout()
  const navigate = useNavigate()
  const { t } = useTranslation()

  return (
    <header className="flex h-14 items-center gap-3 border-b border-border bg-bg px-4">
      <Button variant="ghost" size="sm" onClick={toggleSidebar} aria-label={t('topbar.toggleSidebar')}>
        <Menu className="h-4 w-4" />
      </Button>

      <button
        onClick={() => setCommandPaletteOpen(true)}
        className="flex h-9 flex-1 max-w-md items-center gap-2 rounded-lg border border-border bg-surface px-3 text-sm text-text-muted transition-colors hover:border-primary/50 hover:text-text"
      >
        <Search className="h-4 w-4 shrink-0" />
        <span className="truncate whitespace-nowrap">{t('topbar.searchPlaceholder')}</span>
        <kbd className="ml-auto shrink-0 rounded border border-border bg-card px-1.5 py-0.5 font-mono text-[10px]">⌘K</kbd>
      </button>

      <div className="ml-auto flex items-center gap-2">
        <Button variant="secondary" size="sm" onClick={() => setAiTutorOpen(true)} className="border-primary/30">
          <Sparkles className="h-3.5 w-3.5 text-primary" /> {t('topbar.aiTutor')}
        </Button>
        <Button variant="ghost" size="sm" onClick={toggleTheme} aria-label={t('topbar.toggleTheme')}>
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>

        {user ? (
          <>
            <Button variant="ghost" size="sm" onClick={() => navigate('/settings')} aria-label={t('topbar.settings')}>
              <Settings className="h-4 w-4" />
            </Button>
            <button
              onClick={() => navigate('/settings')}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-forge font-mono text-xs font-semibold text-white shadow-glow transition-transform hover:scale-105"
              title={user.display_name ?? user.email}
            >
              {(user.display_name ?? user.email).slice(0, 2).toUpperCase()}
            </button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => logout.mutate(undefined, { onSuccess: () => navigate('/login') })}
              aria-label={t('topbar.logOut')}
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </>
        ) : (
          <Button size="sm" onClick={() => navigate('/login')}>
            {t('topbar.signIn')}
          </Button>
        )}
      </div>
    </header>
  )
}
