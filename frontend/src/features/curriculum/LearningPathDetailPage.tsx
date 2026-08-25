import { Clock } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { useLearningPath } from '@/hooks/useCurriculum'

export function LearningPathDetailPage() {
  const { slug = '' } = useParams()
  const { data: path, isLoading } = useLearningPath(slug)

  if (isLoading) return <Skeleton className="h-64" />
  if (!path) return <p className="text-sm text-text-muted">Learning path not found.</p>

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-2 text-xl font-bold text-text">{path.title}</h1>
      <p className="mb-6 text-sm text-text-muted">{path.description}</p>

      <div className="space-y-3">
        {path.courses.map((course, i) => (
          <Link key={course.id} to={`/courses/${course.slug}`}>
            <Card className="flex items-center gap-4 transition-colors hover:border-primary/50">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-soft font-mono text-xs font-bold text-primary">
                {i + 1}
              </div>
              <div className="flex-1">
                <h2 className="font-semibold text-text">{course.title}</h2>
                <p className="text-sm text-text-muted">{course.description}</p>
              </div>
              <div className="flex flex-col items-end gap-1">
                <Badge tone="primary">{course.level}</Badge>
                {course.estimated_hours && (
                  <span className="flex items-center gap-1 text-xs text-text-muted">
                    <Clock className="h-3 w-3" />
                    {course.estimated_hours}h
                  </span>
                )}
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
