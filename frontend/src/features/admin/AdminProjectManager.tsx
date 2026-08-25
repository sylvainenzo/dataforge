import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Pencil, Plus, Trash2 } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Skeleton } from '@/components/ui/Skeleton'
import { adminApi, type AdminProject, type AdminProjectSubmission } from '@/services/adminApi'

const DIFFICULTIES = ['beginner', 'intermediate', 'advanced']
const PROJECT_TYPES = ['eda', 'dashboard', 'sql_analysis', 'statistical_analysis', 'ml_model', 'capstone']
const SUBMISSION_STATUSES = ['submitted', 'reviewed', 'passed']

const STATUS_TONE: Record<string, 'neutral' | 'warning' | 'success'> = {
  submitted: 'neutral',
  reviewed: 'warning',
  passed: 'success',
}

function ProjectRow({ project, onChanged }: { project: AdminProject; onChanged: () => void }) {
  const [editing, setEditing] = useState(false)
  const [description, setDescription] = useState(project.description)

  const updateMutation = useMutation({
    mutationFn: () => adminApi.updateProject(project.id, { description }),
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
  })
  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteProject(project.id),
    onSuccess: onChanged,
  })

  return (
    <div className="rounded-lg border border-border p-3">
      <div className="flex items-center gap-2">
        <span className="flex-1 text-sm font-medium text-text">{project.title}</span>
        <Badge tone="primary">{project.difficulty}</Badge>
        <Badge tone="neutral">{project.project_type.replace(/_/g, ' ')}</Badge>
        <button onClick={() => setEditing(!editing)} className="text-text-muted hover:text-primary">
          <Pencil className="h-3.5 w-3.5" />
        </button>
        <button onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending} className="text-text-muted hover:text-error">
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
      {editing ? (
        <div className="mt-2 flex flex-col gap-2">
          <Input value={description} onChange={(e) => setDescription(e.target.value)} />
          <div className="flex gap-2">
            <Button size="sm" disabled={updateMutation.isPending} onClick={() => updateMutation.mutate()}>
              Save
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <p className="mt-1 text-xs text-text-muted">{project.description}</p>
      )}
    </div>
  )
}

function NewProjectForm({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [difficulty, setDifficulty] = useState('beginner')
  const [projectType, setProjectType] = useState('eda')

  const createMutation = useMutation({
    mutationFn: () =>
      adminApi.createProject({ title, description, difficulty, project_type: projectType, rubric: {} }),
    onSuccess: () => {
      setTitle('')
      setDescription('')
      setOpen(false)
      onCreated()
    },
  })

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
        <Plus className="h-3 w-3" /> Add project
      </button>
    )
  }

  return (
    <form
      onSubmit={(e: FormEvent) => {
        e.preventDefault()
        createMutation.mutate()
      }}
      className="flex flex-col gap-2 rounded-lg border border-border p-3"
    >
      <Input placeholder="Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
      <Input placeholder="Description" required value={description} onChange={(e) => setDescription(e.target.value)} />
      <div className="flex gap-2">
        <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="h-10 flex-1 rounded-lg border border-border bg-surface px-3 text-sm text-text">
          {DIFFICULTIES.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
        <select value={projectType} onChange={(e) => setProjectType(e.target.value)} className="h-10 flex-1 rounded-lg border border-border bg-surface px-3 text-sm text-text">
          {PROJECT_TYPES.map((t) => (
            <option key={t} value={t}>
              {t.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
      </div>
      <p className="text-xs text-text-muted">Rubric (objectives, steps, deliverables, etc.) can be added afterward — see docs/DATAFORGE_V2_AUDIT.md for the seed-script pattern used for the built-in projects.</p>
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={createMutation.isPending}>
          Create
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={() => setOpen(false)}>
          Cancel
        </Button>
      </div>
    </form>
  )
}

function ProjectsSection() {
  const queryClient = useQueryClient()
  const { data: projects, isLoading } = useQuery({ queryKey: ['admin', 'projects'], queryFn: adminApi.projects })

  function onChanged() {
    queryClient.invalidateQueries({ queryKey: ['admin', 'projects'] })
    queryClient.invalidateQueries({ queryKey: ['projects'] })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Projects</CardTitle>
      </CardHeader>
      {isLoading ? (
        <Skeleton className="h-24" />
      ) : (
        <div className="flex flex-col gap-2">
          {projects?.map((p) => (
            <ProjectRow key={p.id} project={p} onChanged={onChanged} />
          ))}
          <NewProjectForm onCreated={onChanged} />
        </div>
      )}
    </Card>
  )
}

function SubmissionRow({ submission, onChanged }: { submission: AdminProjectSubmission; onChanged: () => void }) {
  const [status, setStatus] = useState(submission.status)
  const [feedback, setFeedback] = useState(submission.feedback ?? '')

  const reviewMutation = useMutation({
    mutationFn: () => adminApi.reviewSubmission(submission.id, { status, feedback: feedback || undefined }),
    onSuccess: onChanged,
  })

  return (
    <div className="rounded-lg border border-border p-3">
      <div className="flex items-center gap-2">
        <span className="flex-1 text-sm font-medium text-text">{submission.project_title}</span>
        <span className="text-xs text-text-muted">{submission.user_email}</span>
        <Badge tone={STATUS_TONE[submission.status]}>{submission.status}</Badge>
      </div>
      <a href={submission.submission_url ?? undefined} target="_blank" rel="noreferrer" className="mt-1 block truncate text-xs text-primary hover:underline">
        {submission.submission_url}
      </a>
      <div className="mt-2 flex flex-col gap-2">
        <div className="flex gap-2">
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as typeof status)}
            className="h-9 rounded-lg border border-border bg-surface px-2 text-xs text-text"
          >
            {SUBMISSION_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <div className="flex-1">
            <Input placeholder="Feedback" value={feedback} onChange={(e) => setFeedback(e.target.value)} />
          </div>
          <Button size="sm" disabled={reviewMutation.isPending} onClick={() => reviewMutation.mutate()}>
            Save review
          </Button>
        </div>
      </div>
    </div>
  )
}

function SubmissionsSection() {
  const queryClient = useQueryClient()
  const { data: submissions, isLoading } = useQuery({
    queryKey: ['admin', 'project-submissions'],
    queryFn: adminApi.submissions,
  })

  function onChanged() {
    queryClient.invalidateQueries({ queryKey: ['admin', 'project-submissions'] })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Project Submissions</CardTitle>
      </CardHeader>
      {isLoading ? (
        <Skeleton className="h-24" />
      ) : !submissions || submissions.length === 0 ? (
        <p className="text-sm text-text-muted">No submissions yet.</p>
      ) : (
        <div className="flex flex-col gap-2">
          {submissions.map((s) => (
            <SubmissionRow key={s.id} submission={s} onChanged={onChanged} />
          ))}
        </div>
      )}
    </Card>
  )
}

export function AdminProjectManager() {
  return (
    <div className="flex flex-col gap-4">
      <ProjectsSection />
      <SubmissionsSection />
    </div>
  )
}
