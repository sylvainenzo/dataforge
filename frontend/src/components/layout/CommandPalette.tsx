import * as Dialog from '@radix-ui/react-dialog'
import { useQuery } from '@tanstack/react-query'
import { BookMarked, BookOpen, ExternalLink, FolderKanban, Search, Wrench } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { searchApi } from '@/services/searchApi'
import { useUiStore } from '@/stores/uiStore'
import type { SearchResult } from '@/types/search'

const TYPE_ICON: Record<SearchResult['type'], typeof BookOpen> = {
  course: BookOpen,
  lesson: BookOpen,
  tool: Wrench,
  project: FolderKanban,
  resource: ExternalLink,
  glossary_term: BookMarked,
}

function resultHref(result: SearchResult): string {
  if (result.external_url) return result.external_url
  switch (result.type) {
    case 'course':
      return `/courses/${result.slug}`
    case 'lesson':
      return `/lessons/${result.slug}`
    case 'tool':
      return `/tools/${result.slug}`
    case 'project':
      return `/projects/${result.slug}`
    case 'glossary_term':
      return '/resources'
    default:
      return '/'
  }
}

export function CommandPalette() {
  const open = useUiStore((s) => s.commandPaletteOpen)
  const setOpen = useUiStore((s) => s.setCommandPaletteOpen)
  const navigate = useNavigate()
  const { t } = useTranslation()

  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 200)
    return () => clearTimeout(timer)
  }, [query])

  useEffect(() => {
    if (!open) {
      setQuery('')
      setDebouncedQuery('')
    }
  }, [open])

  const { data: results, isFetching } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => searchApi.search(debouncedQuery),
    enabled: debouncedQuery.trim().length > 0,
  })

  function go(result: SearchResult) {
    const href = resultHref(result)
    setOpen(false)
    if (result.external_url) {
      window.open(href, '_blank', 'noreferrer')
    } else {
      navigate(href)
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50" />
        <Dialog.Content className="fixed left-1/2 top-24 z-50 w-full max-w-lg -translate-x-1/2 rounded-xl border border-border bg-card p-2 shadow-xl">
          <Dialog.Title className="sr-only">Search DataForge</Dialog.Title>
          <div className="flex items-center gap-2 border-b border-border px-3 py-2.5">
            <Search className="h-4 w-4 text-text-muted" />
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t('search.placeholder')}
              className="flex-1 bg-transparent text-sm text-text placeholder:text-text-muted focus:outline-none"
            />
          </div>

          <div className="max-h-96 overflow-y-auto">
            {debouncedQuery.trim().length === 0 ? (
              <p className="px-3 py-6 text-center text-sm text-text-muted">{t('search.prompt')}</p>
            ) : isFetching ? (
              <p className="px-3 py-6 text-center text-sm text-text-muted">{t('search.searching')}</p>
            ) : !results || results.length === 0 ? (
              <p className="px-3 py-6 text-center text-sm text-text-muted">
                {t('search.noResults', { query: debouncedQuery })}
              </p>
            ) : (
              <ul className="py-1">
                {results.map((r, i) => {
                  const Icon = TYPE_ICON[r.type]
                  return (
                    <li key={`${r.type}-${r.slug ?? r.external_url}-${i}`}>
                      <button
                        onClick={() => go(r)}
                        className="flex w-full items-start gap-3 rounded-lg px-3 py-2 text-left hover:bg-surface"
                      >
                        <Icon className="mt-0.5 h-4 w-4 shrink-0 text-text-muted" />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="truncate text-sm font-medium text-text">{r.title}</span>
                            <span className="shrink-0 rounded bg-surface px-1.5 py-0.5 font-mono text-[10px] uppercase text-text-muted">
                              {t(`search.${r.type}`)}
                            </span>
                          </div>
                          {r.subtitle && <p className="truncate text-xs text-text-muted">{r.subtitle}</p>}
                        </div>
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
