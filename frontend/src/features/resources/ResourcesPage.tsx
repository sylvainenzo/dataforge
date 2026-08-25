import { useQuery } from '@tanstack/react-query'
import { BookMarked, ExternalLink, Library } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { knowledgeBaseApi } from '@/services/knowledgeBaseApi'

export function ResourcesPage() {
  const { data: resources, isLoading: resourcesLoading } = useQuery({
    queryKey: ['resources'],
    queryFn: knowledgeBaseApi.resources,
  })
  const { data: glossary, isLoading: glossaryLoading } = useQuery({
    queryKey: ['glossary'],
    queryFn: knowledgeBaseApi.glossary,
  })

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6">
      <h1 className="text-xl font-bold text-text">Resources</h1>

      <Card>
        <CardHeader>
          <CardTitle>External Learning Resources</CardTitle>
          <Library className="h-4 w-4 text-text-muted" />
        </CardHeader>

        {resourcesLoading ? (
          <Skeleton className="h-32" />
        ) : !resources || resources.length === 0 ? (
          <EmptyState icon={Library} title="No resources yet" description="Curated external resources appear here." />
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {resources.map((r) => (
              <a
                key={r.id}
                href={r.url}
                target="_blank"
                rel="noreferrer"
                className="flex flex-col gap-2 rounded-lg border border-border p-3 transition-colors hover:border-primary/50"
              >
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-medium text-text">{r.title}</h3>
                  <ExternalLink className="h-3.5 w-3.5 shrink-0 text-text-muted" />
                </div>
                <p className="text-xs text-text-muted">{r.provider}</p>
                {r.description && <p className="text-sm text-text-muted">{r.description}</p>}
                <div className="mt-auto flex gap-2 pt-1">
                  <Badge tone="primary">{r.level}</Badge>
                  {r.is_free && <Badge tone="success">Free</Badge>}
                </div>
              </a>
            ))}
          </div>
        )}
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Glossary</CardTitle>
          <BookMarked className="h-4 w-4 text-text-muted" />
        </CardHeader>

        {glossaryLoading ? (
          <Skeleton className="h-32" />
        ) : !glossary || glossary.length === 0 ? (
          <EmptyState icon={BookMarked} title="No terms yet" description="Key terms from the curriculum appear here." />
        ) : (
          <div className="divide-y divide-border">
            {glossary.map((t) => (
              <details key={t.id} className="group py-3 first:pt-0 last:pb-0">
                <summary className="cursor-pointer list-none font-medium text-text marker:content-none">
                  <span className="mr-2 text-text-muted group-open:hidden">▸</span>
                  <span className="mr-2 hidden text-text-muted group-open:inline">▾</span>
                  {t.term}
                </summary>
                <div className="mt-2 space-y-2 pl-5 text-sm">
                  <p className="text-text-muted">{t.simple_explanation}</p>
                  {t.technical_explanation && (
                    <p className="text-text-muted">
                      <span className="font-semibold text-text">Technical: </span>
                      {t.technical_explanation}
                    </p>
                  )}
                  {t.example && (
                    <pre className="overflow-x-auto rounded-md bg-surface p-2 font-mono text-xs text-text">{t.example}</pre>
                  )}
                </div>
              </details>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
