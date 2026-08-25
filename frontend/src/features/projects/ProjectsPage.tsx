import { useQuery } from '@tanstack/react-query'
import { FolderKanban } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { projectsApi } from '@/services/projectsApi'

export function ProjectsPage() {
  const { data: projects, isLoading } = useQuery({ queryKey: ['projects'], queryFn: projectsApi.list })

  if (isLoading) return <Skeleton className="h-32" />

  if (!projects || projects.length === 0) {
    return <EmptyState icon={FolderKanban} title="No projects yet" description="Scoped, dataset-backed projects appear here." />
  }

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="mb-4 text-xl font-bold text-text">Projects</h1>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {projects.map((p) => (
          <Link key={p.id} to={`/projects/${p.slug}`}>
            <Card className="h-full transition-colors hover:border-primary/50">
              <div className="mb-2 flex gap-2">
                <Badge tone="primary">{p.difficulty}</Badge>
                <Badge tone="neutral">{p.project_type.replace(/_/g, ' ')}</Badge>
              </div>
              <h2 className="mb-1 font-semibold text-text">{p.title}</h2>
              <p className="text-sm text-text-muted">{p.description}</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
