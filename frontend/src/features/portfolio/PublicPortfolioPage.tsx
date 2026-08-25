import { useQuery } from '@tanstack/react-query'
import { Award, ExternalLink, FolderKanban, ShieldOff, UserRound } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { ApiError } from '@/lib/api'
import { portfolioApi } from '@/services/portfolioApi'

export function PublicPortfolioPage() {
  const { userId = '' } = useParams()
  const { data: portfolio, isLoading, error } = useQuery({
    queryKey: ['portfolio', 'public', userId],
    queryFn: () => portfolioApi.public(userId),
    retry: false,
  })

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (error || !portfolio) {
    const notFound = error instanceof ApiError && error.status === 404
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-bg px-4 text-center">
        <ShieldOff className="h-8 w-8 text-text-muted" />
        <p className="text-sm font-semibold text-text">
          {notFound ? 'This portfolio is private or does not exist.' : 'Could not load this portfolio.'}
        </p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-bg px-4 py-12">
      <div className="mx-auto max-w-2xl">
        <div className="mb-8 flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary-soft">
            <UserRound className="h-7 w-7 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-text">{portfolio.display_name}</h1>
            {portfolio.bio && <p className="mt-1 text-sm text-text-muted">{portfolio.bio}</p>}
          </div>
        </div>

        <div className="mb-8">
          <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-text-muted">
            <FolderKanban className="h-4 w-4" /> Projects
          </h2>
          {portfolio.projects.length === 0 ? (
            <p className="text-sm text-text-muted">No passed projects yet.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {portfolio.projects.map((p) => (
                <Card key={p.project_slug} className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-medium text-text">{p.project_title}</p>
                    {p.reviewed_at && (
                      <p className="text-xs text-text-muted">Passed {new Date(p.reviewed_at).toLocaleDateString()}</p>
                    )}
                  </div>
                  {p.submission_url && (
                    <a
                      href={p.submission_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-sm text-text-muted hover:border-primary hover:text-primary"
                    >
                      <ExternalLink className="h-3.5 w-3.5" /> View
                    </a>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>

        <div>
          <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-text-muted">
            <Award className="h-4 w-4" /> Certificates
          </h2>
          {portfolio.certificates.length === 0 ? (
            <p className="text-sm text-text-muted">No certificates yet.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {portfolio.certificates.map((c) => (
                <Card key={c.certificate_number} className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent-soft">
                    <Award className="h-5 w-5 text-accent" />
                  </div>
                  <div>
                    <p className="font-medium text-text">{c.course_title}</p>
                    <p className="font-mono text-xs text-text-muted">
                      {c.certificate_number} · issued {new Date(c.issued_at).toLocaleDateString()}
                    </p>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
