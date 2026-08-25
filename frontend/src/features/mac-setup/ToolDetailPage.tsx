import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, ExternalLink } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { toolsApi } from '@/services/toolsApi'

export function ToolDetailPage() {
  const { slug = '' } = useParams()
  const { data: tool, isLoading } = useQuery({ queryKey: ['tools', slug], queryFn: () => toolsApi.detail(slug) })

  if (isLoading) return <Skeleton className="h-64" />
  if (!tool) return <p className="text-sm text-text-muted">Tool not found.</p>

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-1 flex items-center gap-2">
        <h1 className="text-xl font-bold text-text">{tool.name}</h1>
        <Badge tone="neutral">{tool.category}</Badge>
      </div>
      <p className="mb-6 text-sm text-text-muted">{tool.description}</p>

      <div className="space-y-4">
        {tool.homebrew_command && (
          <Card>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-muted">Install</p>
            <pre className="overflow-x-auto rounded-lg bg-surface p-3 font-mono text-sm text-text">
              <code>{tool.homebrew_command}</code>
            </pre>
          </Card>
        )}

        {tool.verification_command && (
          <Card>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-muted">Verify it worked</p>
            <pre className="overflow-x-auto rounded-lg bg-surface p-3 font-mono text-sm text-text">
              <code>{tool.verification_command}</code>
            </pre>
          </Card>
        )}

        {tool.common_errors && Object.keys(tool.common_errors).length > 0 && (
          <Card>
            <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-text-muted">
              <AlertTriangle className="h-3.5 w-3.5 text-warning" /> Common errors
            </div>
            <dl className="space-y-3">
              {Object.entries(tool.common_errors).map(([error, fix]) => (
                <div key={error}>
                  <dt className="font-mono text-xs text-error">{error}</dt>
                  <dd className="mt-0.5 text-sm text-text-muted">{fix}</dd>
                </div>
              ))}
            </dl>
          </Card>
        )}

        {tool.alternatives && tool.alternatives.length > 0 && (
          <Card>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-muted">Alternatives</p>
            <p className="text-sm text-text-muted">{tool.alternatives.join(', ')}</p>
          </Card>
        )}

        <a
          href={tool.official_url}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1 text-sm font-medium text-primary hover:underline"
        >
          Official site <ExternalLink className="h-3.5 w-3.5" />
        </a>
        <p className="text-xs text-text-muted">Last verified {tool.last_verified_at}</p>
      </div>
    </div>
  )
}
