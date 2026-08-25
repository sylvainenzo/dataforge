import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { BookOpen, Code2, Database, FolderKanban, GraduationCap, ShieldCheck, Users } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Skeleton } from '@/components/ui/Skeleton'
import { useCurrentUser } from '@/hooks/useAuth'
import { adminApi } from '@/services/adminApi'
import { AdminCourseManager } from '@/features/admin/AdminCourseManager'
import { AdminKnowledgeCareerManager } from '@/features/admin/AdminKnowledgeCareerManager'
import { AdminProjectManager } from '@/features/admin/AdminProjectManager'

const ASSIGNABLE_ROLES = ['student', 'instructor', 'admin']

function StatCard({ icon: Icon, label, value }: { icon: typeof Users; label: string; value: number }) {
  return (
    <Card className="flex items-center gap-3">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-soft">
        <Icon className="h-4 w-4 text-primary" />
      </div>
      <div>
        <p className="font-mono text-lg font-bold text-text">{value}</p>
        <p className="text-xs text-text-muted">{label}</p>
      </div>
    </Card>
  )
}

export function AdminPage() {
  const { user } = useCurrentUser()
  const queryClient = useQueryClient()
  const { data: stats, isLoading: statsLoading } = useQuery({ queryKey: ['admin', 'stats'], queryFn: adminApi.stats })
  const { data: users, isLoading: usersLoading } = useQuery({ queryKey: ['admin', 'users'], queryFn: adminApi.users })

  const [title, setTitle] = useState('')
  const [hours, setHours] = useState('')
  const [courseError, setCourseError] = useState<string | null>(null)
  const [courseSuccess, setCourseSuccess] = useState<string | null>(null)

  const roleMutation = useMutation({
    mutationFn: ({ userId, role, grant }: { userId: string; role: string; grant: boolean }) =>
      adminApi.setUserRole(userId, role, grant),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'users'] }),
  })

  async function onCreateCourse(e: FormEvent) {
    e.preventDefault()
    setCourseError(null)
    setCourseSuccess(null)
    try {
      const course = await adminApi.createCourse({
        title,
        level: 'beginner',
        estimated_hours: hours ? Number(hours) : undefined,
        published: true,
      })
      setCourseSuccess(`Created "${course.title}" (${course.slug})`)
      setTitle('')
      setHours('')
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] })
      queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] })
    } catch {
      setCourseError('Could not create course.')
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-1 flex items-center gap-2">
        <ShieldCheck className="h-5 w-5 text-primary" />
        <h1 className="text-xl font-bold text-text">Admin</h1>
      </div>
      <p className="mb-6 text-sm text-text-muted">Real content management — every number and row below comes from the live database.</p>

      {statsLoading ? (
        <Skeleton className="h-24" />
      ) : (
        stats && (
          <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard icon={Users} label="Users" value={stats.user_count} />
            <StatCard icon={BookOpen} label="Courses" value={stats.course_count} />
            <StatCard icon={GraduationCap} label="Lessons" value={stats.lesson_count} />
            <StatCard icon={Database} label="Datasets" value={stats.dataset_count} />
            <StatCard icon={FolderKanban} label="Projects" value={stats.project_count} />
            <StatCard icon={Code2} label="Code runs" value={stats.code_execution_count} />
          </div>
        )
      )}

      <Card className="mb-6">
        <h2 className="mb-3 text-sm font-semibold text-text">Create a course</h2>
        <form onSubmit={onCreateCourse} className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <Input label="Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="w-32">
            <Input label="Hours" type="number" value={hours} onChange={(e) => setHours(e.target.value)} />
          </div>
          <Button type="submit">Create</Button>
        </form>
        {courseError && <p className="mt-2 text-sm text-error">{courseError}</p>}
        {courseSuccess && <p className="mt-2 text-sm text-success">{courseSuccess}</p>}
      </Card>

      <div className="mb-6">
        <h2 className="mb-3 text-sm font-semibold text-text">Manage courses</h2>
        <AdminCourseManager />
      </div>

      <div className="mb-6">
        <h2 className="mb-3 text-sm font-semibold text-text">Manage content</h2>
        <AdminKnowledgeCareerManager />
      </div>

      <div className="mb-6">
        <h2 className="mb-3 text-sm font-semibold text-text">Manage projects</h2>
        <AdminProjectManager />
      </div>

      <Card>
        <h2 className="mb-3 text-sm font-semibold text-text">Users</h2>
        {usersLoading ? (
          <Skeleton className="h-32" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-border text-xs uppercase text-text-muted">
                  <th className="px-2 py-1.5">Email</th>
                  <th className="px-2 py-1.5">Roles</th>
                  <th className="px-2 py-1.5">Manage</th>
                </tr>
              </thead>
              <tbody>
                {users?.map((u) => (
                  <tr key={u.id} className="border-b border-border last:border-0">
                    <td className="px-2 py-2 text-text">{u.email}</td>
                    <td className="px-2 py-2">
                      <div className="flex gap-1">
                        {u.roles.map((r) => (
                          <Badge key={r} tone="primary">
                            {r}
                          </Badge>
                        ))}
                      </div>
                    </td>
                    <td className="px-2 py-2">
                      <div className="flex gap-1">
                        {ASSIGNABLE_ROLES.filter((r) => !u.roles.includes(r)).map((r) => (
                          <button
                            key={r}
                            disabled={roleMutation.isPending}
                            onClick={() => roleMutation.mutate({ userId: u.id, role: r, grant: true })}
                            className="rounded-md border border-border px-2 py-1 text-xs text-text-muted hover:border-primary hover:text-primary disabled:opacity-50"
                          >
                            + {r}
                          </button>
                        ))}
                        {u.roles
                          .filter((r) => !(r === 'admin' && u.id === user?.id))
                          .map((r) => (
                            <button
                              key={r}
                              disabled={roleMutation.isPending}
                              onClick={() => roleMutation.mutate({ userId: u.id, role: r, grant: false })}
                              className="rounded-md border border-error/30 px-2 py-1 text-xs text-error hover:bg-error-soft disabled:opacity-50"
                            >
                              − {r}
                            </button>
                          ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
