import { Suspense, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { AiTutorPanel } from '@/components/layout/AiTutorPanel'
import { CommandPalette } from '@/components/layout/CommandPalette'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { Skeleton } from '@/components/ui/Skeleton'
import { useCurrentUser } from '@/hooks/useAuth'
import { useUiStore } from '@/stores/uiStore'

export function AppLayout() {
  const { user } = useCurrentUser()
  const setCommandPaletteOpen = useUiStore((s) => s.setCommandPaletteOpen)

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(true)
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [setCommandPaletteOpen])

  return (
    <div className="flex h-screen bg-bg">
      <Sidebar user={user} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar user={user} />
        <main className="flex-1 overflow-y-auto p-6">
          <Suspense fallback={<Skeleton className="h-64 w-full" />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
      <CommandPalette />
      <AiTutorPanel />
    </div>
  )
}
