import {
  Award,
  BookOpen,
  Briefcase,
  Database,
  FlaskConical,
  FolderKanban,
  Laptop,
  Layers,
  LayoutDashboard,
  Library,
  MessageCircleQuestion,
  Shield,
  Sparkles,
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/cn'
import { useUiStore } from '@/stores/uiStore'
import type { User } from '@/types/auth'

interface NavItem {
  to: string
  labelKey: string
  icon: typeof LayoutDashboard
  adminOnly?: boolean
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', labelKey: 'nav.dashboard', icon: LayoutDashboard },
  { to: '/courses', labelKey: 'nav.courses', icon: BookOpen },
  { to: '/learning-paths', labelKey: 'nav.learningPaths', icon: Layers },
  { to: '/labs', labelKey: 'nav.labs', icon: FlaskConical },
  { to: '/flashcards', labelKey: 'nav.flashcards', icon: Sparkles },
  { to: '/projects', labelKey: 'nav.projects', icon: FolderKanban },
  { to: '/datasets', labelKey: 'nav.datasets', icon: Database },
  { to: '/resources', labelKey: 'nav.resources', icon: Library },
  { to: '/career', labelKey: 'nav.career', icon: Briefcase },
  { to: '/interview-questions', labelKey: 'nav.interviewQuestions', icon: MessageCircleQuestion },
  { to: '/mac-setup', labelKey: 'nav.macSetup', icon: Laptop },
  { to: '/certificates', labelKey: 'nav.certificates', icon: Award },
  { to: '/admin', labelKey: 'nav.admin', icon: Shield, adminOnly: true },
]

export function Sidebar({ user }: { user: User | null }) {
  const collapsed = useUiStore((s) => s.sidebarCollapsed)
  const isAdmin = user?.roles.includes('admin') ?? false
  const { t } = useTranslation()

  return (
    <aside
      className={cn(
        'flex h-screen flex-col border-r border-border bg-surface transition-[width]',
        collapsed ? 'w-16' : 'w-60',
      )}
    >
      <div className="flex h-14 items-center gap-2 border-b border-border px-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary font-mono text-xs font-bold text-white">
          DF
        </div>
        {!collapsed && <span className="text-sm font-bold tracking-tight text-text">DataForge</span>}
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto p-2">
        {NAV_ITEMS.filter((item) => !item.adminOnly || isAdmin).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive ? 'bg-primary-soft text-primary' : 'text-text-muted hover:bg-card hover:text-text',
              )
            }
          >
            <item.icon className="h-4 w-4 shrink-0" strokeWidth={1.75} />
            {!collapsed && <span>{t(item.labelKey)}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
