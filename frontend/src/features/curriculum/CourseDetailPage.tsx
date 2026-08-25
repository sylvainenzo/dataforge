import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Award, CheckCircle2, Circle, Download } from 'lucide-react'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useCourse } from '@/hooks/useCurriculum'
import { ApiError } from '@/lib/api'
import { certificatesApi } from '@/services/certificatesApi'

function CertificateSection({ courseId, slug }: { courseId: string; slug: string }) {
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const { data: certificates } = useQuery({ queryKey: ['certificates'], queryFn: certificatesApi.list })

  const issueMutation = useMutation({
    mutationFn: () => certificatesApi.issue(slug),
    onSuccess: () => {
      setError(null)
      queryClient.invalidateQueries({ queryKey: ['certificates'] })
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Could not issue certificate.'),
  })

  const existing = certificates?.find((c) => c.course_id === courseId)

  return (
    <Card className="mb-6">
      <div className="flex items-center gap-3">
        <Award className="h-5 w-5 shrink-0 text-accent" />
        <div className="flex-1">
          <h2 className="text-sm font-semibold text-text">Certificate of completion</h2>
          <p className="text-xs text-text-muted">
            {existing
              ? `Issued ${new Date(existing.issued_at).toLocaleDateString()}.`
              : 'Complete every lesson in this course to unlock it.'}
          </p>
        </div>
        {!existing && (
          <Button size="sm" disabled={issueMutation.isPending} onClick={() => issueMutation.mutate()}>
            Get certificate
          </Button>
        )}
      </div>
      {error && <p className="mt-2 text-xs text-error">{error}</p>}
      {existing && (
        <a
          href={certificatesApi.downloadUrl(existing.id)}
          className="mt-3 flex items-center gap-2 text-sm text-primary hover:underline"
        >
          <Download className="h-3.5 w-3.5" /> Download {existing.certificate_number}
        </a>
      )}
    </Card>
  )
}

export function CourseDetailPage() {
  const { slug = '' } = useParams()
  const { data: course, isLoading } = useCourse(slug)

  if (isLoading) return <Skeleton className="h-64" />
  if (!course) return <p className="text-sm text-text-muted">Course not found.</p>

  return (
    <div className="mx-auto max-w-3xl">
      <Badge tone="primary" className="mb-2">
        {course.level}
      </Badge>
      <h1 className="mb-2 text-xl font-bold text-text">{course.title}</h1>
      <p className="mb-6 text-sm text-text-muted">{course.description}</p>

      <div className="space-y-6">
        {course.modules.map((module) => (
          <div key={module.id}>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-text-muted">{module.title}</h2>
            <div className="divide-y divide-border overflow-hidden rounded-xl border border-border bg-card">
              {module.lessons.map((lesson) => {
                const completed = course.completed_lesson_ids.includes(lesson.id)
                return (
                  <Link
                    key={lesson.id}
                    to={`/lessons/${lesson.slug}`}
                    className="flex items-center gap-3 px-4 py-3 text-sm text-text transition-colors hover:bg-surface"
                  >
                    {completed ? (
                      <CheckCircle2 className="h-4 w-4 shrink-0 text-success" />
                    ) : (
                      <Circle className="h-4 w-4 shrink-0 text-text-muted" />
                    )}
                    <span className="flex-1">{lesson.title}</span>
                    {lesson.estimated_minutes && (
                      <span className="text-xs text-text-muted">{lesson.estimated_minutes} min</span>
                    )}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6">
        <CertificateSection courseId={course.id} slug={slug} />
      </div>
    </div>
  )
}
