import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'dark' | 'light'
export type Language = 'en' | 'fr'

interface UiState {
  theme: Theme
  language: Language
  sidebarCollapsed: boolean
  commandPaletteOpen: boolean
  aiTutorOpen: boolean
  toggleTheme: () => void
  setLanguage: (language: Language) => void
  toggleSidebar: () => void
  setCommandPaletteOpen: (open: boolean) => void
  setAiTutorOpen: (open: boolean) => void
}

/** Deliberately small — Phase 1 §4: global Zustand state is limited to
 * genuinely global client-only UI state. Anything server-derived (the
 * current user, curriculum, progress) lives in TanStack Query instead. */
export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      theme: 'dark',
      language: 'en',
      sidebarCollapsed: false,
      commandPaletteOpen: false,
      aiTutorOpen: false,
      toggleTheme: () => set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),
      setLanguage: (language) => set({ language }),
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
      setAiTutorOpen: (open) => set({ aiTutorOpen: open }),
    }),
    {
      name: 'dataforge-ui',
      partialize: (s) => ({ theme: s.theme, language: s.language, sidebarCollapsed: s.sidebarCollapsed }),
    },
  ),
)
