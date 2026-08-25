import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Send } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Skeleton } from '@/components/ui/Skeleton'
import { ApiError } from '@/lib/api'
import { projectsApi } from '@/services/projectsApi'

const STATUS_TONE = {
  submitted: 'neutral',
  reviewed: 'warning',
  passed: 'success',
} as const

function SubmissionSection({ slug }: { slug: string }) {
  const queryClient = useQueryClient()
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | null>(null)
  const { data: submissions, isLoading } = useQuery({
    queryKey: ['projects', slug, 'submissions'],
    queryFn: () => projectsApi.mySubmissions(slug),
  })

  const submitMutation = useMutation({
    mutationFn: () => projectsApi.submit(slug, url),
    onSuccess: () => {
      setUrl('')
      queryClient.invalidateQueries({ queryKey: ['projects', slug, 'submissions'] })
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Could not submit.'),
  })

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    submitMutation.mutate()
  }

  return (
    <Card>
      <h2 className="mb-2 text-sm font-semibold text-text">Submit your work</h2>
      <p className="mb-3 text-sm text-text-muted">
        Paste a link to your write-up — a GitHub repo, notebook, or doc — for review.
      </p>
      <form onSubmit={onSubmit} className="flex gap-2">
        <div className="flex-1">
          <Input
            type="url"
            placeholder="https://github.com/you/project"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={submitMutation.isPending}>
          <Send className="h-3.5 w-3.5" /> Submit
        </Button>
      </form>
      {error && <p className="mt-2 text-sm text-error">{error}</p>}

      {isLoading ? (
        <Skeleton className="mt-4 h-16" />
      ) : (
        submissions &&
        submissions.length > 0 && (
          <div className="mt-4 space-y-2 border-t border-border pt-4">
            {submissions.map((s) => (
              <div key={s.id} className="rounded-lg border border-border p-3">
                <div className="flex items-center justify-between gap-2">
                  <a
                    href={s.submission_url ?? undefined}
                    target="_blank"
                    rel="noreferrer"
                    className="truncate text-sm text-primary hover:underline"
                  >
                    {s.submission_url}
                  </a>
                  <Badge tone={STATUS_TONE[s.status]}>{s.status}</Badge>
                </div>
                {s.feedback && <p className="mt-2 text-sm text-text-muted">{s.feedback}</p>}
              </div>
            ))}
          </div>
        )
      )}
    </Card>
  )
}

export function ProjectDetailPage() {
  const { slug = '' } = useParams()
  const { data: project, isLoading } = useQuery({ queryKey: ['projects', slug], queryFn: () => projectsApi.detail(slug) })

  if (isLoading) return <Skeleton className="h-96" />
  if (!project) return <p className="text-sm text-text-muted">Project not found.</p>

  const { rubric } = project

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-2 flex gap-2">
        <Badge tone="primary">{project.difficulty}</Badge>
        <Badge tone="neutral">{project.project_type.replace(/_/g, ' ')}</Badge>
      </div>
      <h1 className="mb-4 text-xl font-bold text-text">{project.title}</h1>

      <Card className="mb-4">
        <h2 className="mb-2 text-sm font-semibold text-text">The problem</h2>
        <p className="text-sm text-text-muted">{rubric.business_problem}</p>
      </Card>

      <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <h2 className="mb-2 text-sm font-semibold text-text">Objectives</h2>
          <ul className="list-inside list-disc space-y-1 text-sm text-text-muted">
            {rubric.objectives.map((o) => (
              <li key={o}>{o}</li>
            ))}
          </ul>
        </Card>
        <Card>
          <h2 className="mb-2 text-sm font-semibold text-text">Questions to answer</h2>
          <ul className="list-inside list-disc space-y-1 text-sm text-text-muted">
            {rubric.questions.map((q) => (
              <li key={q}>{q}</li>
            ))}
          </ul>
        </Card>
      </div>

      <Card className="mb-4">
        <h2 className="mb-2 text-sm font-semibold text-text">Steps</h2>
        <ol className="list-inside list-decimal space-y-1.5 text-sm text-text-muted">
          {rubric.steps.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ol>
      </Card>

      <Card className="mb-4">
        <h2 className="mb-2 text-sm font-semibold text-text">Deliverables</h2>
        <ul className="space-y-1.5 text-sm text-text-muted">
          {rubric.deliverables.map((d) => (
            <li key={d} className="flex items-start gap-2">
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
              {d}
            </li>
          ))}
        </ul>
      </Card>

      <Card className="mb-4">
        <h2 className="mb-2 text-sm font-semibold text-text">How it's evaluated</h2>
        <dl className="space-y-2">
          {Object.entries(rubric.evaluation_rubric).map(([key, desc]) => (
            <div key={key}>
              <dt className="font-mono text-xs text-primary">{key.replace(/_/g, ' ')}</dt>
              <dd className="text-sm text-text-muted">{desc}</dd>
            </div>
          ))}
        </dl>
      </Card>

      <SubmissionSection slug={slug} />
    </div>
  )
}
