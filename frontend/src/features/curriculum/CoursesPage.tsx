import { BookOpen, Clock } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useCourses } from '@/hooks/useCurriculum'

export function CoursesPage() {
  const { data: courses, isLoading } = useCourses()

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    )
  }

  if (!courses || courses.length === 0) {
    return (
      <EmptyState icon={BookOpen} title="No published courses yet" description="Courses appear here once they are authored and published." />
    )
  }

  return (
    <div>
      <h1 className="mb-4 text-xl font-bold text-text">Courses</h1>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {courses.map((course) => (
          <Link key={course.id} to={`/courses/${course.slug}`}>
            <Card className="h-full transition-colors hover:border-primary/50">
              <div className="mb-2 flex items-center justify-between">
                <Badge tone="primary">{course.level}</Badge>
                {course.estimated_hours && (
                  <span className="flex items-center gap-1 text-xs text-text-muted">
                    <Clock className="h-3 w-3" />
                    {course.estimated_hours}h
                  </span>
                )}
              </div>
              <h2 className="mb-1 font-semibold text-text">{course.title}</h2>
              <p className="text-sm text-text-muted">{course.description}</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
