import { useQuery } from '@tanstack/react-query'
import { Briefcase, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/lib/cn'
import { careerApi } from '@/services/careerApi'

function CareerPathProgressPanel({ slug }: { slug: string }) {
  const { data: progress, isLoading } = useQuery({
    queryKey: ['career-paths', slug, 'progress'],
    queryFn: () => careerApi.progress(slug),
  })

  if (isLoading) return <Skeleton className="h-24" />
  if (!progress) return null

  return (
    <div className="space-y-4 border-t border-border pt-4">
      <div>
        <div className="mb-1 flex items-center justify-between text-sm">
          <span className="font-medium text-text">Overall progress</span>
          <span className="font-mono text-text-muted">{Math.round(progress.overall_completion * 100)}%</span>
        </div>
        <ProgressBar value={progress.overall_completion * 100} tone="accent" />
      </div>

      <div className="space-y-3">
        {progress.skills.map((s) => (
          <div key={s.skill_id}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="text-text-muted">
                {s.skill_name} <span className="text-text-muted/60">(weight {s.weight}×)</span>
              </span>
              <span className="font-mono text-text-muted">
                {s.lessons_completed}/{s.lessons_total} lessons
              </span>
            </div>
            <ProgressBar value={s.completion * 100} />
          </div>
        ))}
      </div>
    </div>
  )
}

export function CareerPage() {
  const { data: paths, isLoading } = useQuery({ queryKey: ['career-paths'], queryFn: careerApi.list })
  const [expandedSlug, setExpandedSlug] = useState<string | null>(null)

  if (isLoading) return <Skeleton className="h-32" />

  if (!paths || paths.length === 0) {
    return <EmptyState icon={Briefcase} title="No career paths yet" description="Career-path skill mapping appears here." />
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-1 text-xl font-bold text-text">Career Paths</h1>
      <p className="mb-4 text-sm text-text-muted">
        Pick a track to see how your completed lessons map to the skills it weighs most.
      </p>
      <div className="flex flex-col gap-3">
        {paths.map((p) => {
          const expanded = expandedSlug === p.slug
          return (
            <Card key={p.id}>
              <button
                className="flex w-full items-center justify-between gap-2 text-left"
                onClick={() => setExpandedSlug(expanded ? null : p.slug)}
              >
                <div>
                  <h2 className="font-semibold text-text">{p.name}</h2>
                  {p.description && <p className="mt-1 text-sm text-text-muted">{p.description}</p>}
                </div>
                <ChevronDown className={cn('h-4 w-4 shrink-0 text-text-muted transition-transform', expanded && 'rotate-180')} />
              </button>
              {expanded && (
                <div className="mt-4">
                  <CareerPathProgressPanel slug={p.slug} />
                </div>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
