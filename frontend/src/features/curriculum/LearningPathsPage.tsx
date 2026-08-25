import { Layers } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useLearningPaths } from '@/hooks/useCurriculum'

export function LearningPathsPage() {
  const { data: paths, isLoading } = useLearningPaths()

  if (isLoading) return <Skeleton className="h-32" />

  if (!paths || paths.length === 0) {
    return (
      <EmptyState icon={Layers} title="No learning paths yet" description="Learning paths group courses into a guided track toward a role." />
    )
  }

  return (
    <div>
      <h1 className="mb-4 text-xl font-bold text-text">Learning Paths</h1>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {paths.map((path) => (
          <Link key={path.id} to={`/learning-paths/${path.slug}`}>
            <Card className="h-full transition-colors hover:border-primary/50">
              <h2 className="mb-1 font-semibold text-text">{path.title}</h2>
              <p className="text-sm text-text-muted">{path.description}</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
