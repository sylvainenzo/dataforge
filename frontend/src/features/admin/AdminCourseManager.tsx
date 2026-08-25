import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronDown, Pencil, Plus, Trash2 } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/lib/cn'
import { ApiError } from '@/lib/api'
import { adminApi } from '@/services/adminApi'
import type { AdminCourse, AdminCourseTreeLesson, AdminCourseTreeModule } from '@/types/admin'

const COURSE_LEVELS = ['beginner', 'practical', 'technical', 'advanced', 'professional']

function ErrorText({ message }: { message: string | null }) {
  if (!message) return null
  return <p className="mt-1 text-xs text-error">{message}</p>
}

function QuizEditor({ lesson, onChanged }: { lesson: AdminCourseTreeLesson; onChanged: () => void }) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(lesson.quiz?.title ?? '')
  const [passingScore, setPassingScore] = useState(String(lesson.quiz?.passing_score ?? 70))
  const [questionsJson, setQuestionsJson] = useState(
    JSON.stringify(
      lesson.quiz?.questions.map((q) => ({
        question_text: q.question_text,
        question_type: q.question_type,
        options: q.options,
        correct_answer: q.correct_answer,
        explanation: q.explanation,
        order: q.order,
        points: q.points,
      })) ?? [{ question_text: '', question_type: 'multiple_choice', options: { choices: ['A', 'B'] }, correct_answer: { value: 'A' }, order: 1, points: 1 }],
      null,
      2,
    ),
  )
  const [error, setError] = useState<string | null>(null)

  const createMutation = useMutation({
    mutationFn: () => {
      const questions = JSON.parse(questionsJson)
      return adminApi.createQuiz(lesson.id, { title, passing_score: Number(passingScore), questions })
    },
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Invalid JSON in questions.'),
  })

  const updateMutation = useMutation({
    mutationFn: () => {
      const questions = JSON.parse(questionsJson)
      return adminApi.updateQuiz(lesson.quiz!.id, { title, passing_score: Number(passingScore), questions })
    },
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Invalid JSON in questions.'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteQuiz(lesson.quiz!.id),
    onSuccess: onChanged,
  })

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      JSON.parse(questionsJson)
    } catch {
      setError('Questions must be valid JSON.')
      return
    }
    if (lesson.quiz) updateMutation.mutate()
    else createMutation.mutate()
  }

  if (!editing) {
    return (
      <div className="mt-2 flex items-center gap-2 border-t border-border pt-2">
        {lesson.quiz ? (
          <>
            <span className="text-xs text-text-muted">
              Quiz: <span className="text-text">{lesson.quiz.title}</span> ({lesson.quiz.questions.length} questions, pass{' '}
              {lesson.quiz.passing_score}%)
            </span>
            <button onClick={() => setEditing(true)} className="ml-auto text-text-muted hover:text-primary">
              <Pencil className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
              className="text-text-muted hover:text-error"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </>
        ) : (
          <button onClick={() => setEditing(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
            <Plus className="h-3 w-3" /> Add quiz
          </button>
        )}
      </div>
    )
  }

  return (
    <form onSubmit={onSubmit} className="mt-2 flex flex-col gap-2 border-t border-border pt-2">
      <div className="flex gap-2">
        <div className="flex-1">
          <Input placeholder="Quiz title" required value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="w-28">
          <Input
            type="number"
            placeholder="Pass %"
            required
            value={passingScore}
            onChange={(e) => setPassingScore(e.target.value)}
          />
        </div>
      </div>
      <textarea
        value={questionsJson}
        onChange={(e) => setQuestionsJson(e.target.value)}
        rows={8}
        className="rounded-lg border border-border bg-surface p-2 font-mono text-xs text-text"
        placeholder="Questions as JSON array"
      />
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={createMutation.isPending || updateMutation.isPending}>
          Save quiz
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={() => setEditing(false)}>
          Cancel
        </Button>
      </div>
      <ErrorText message={error} />
    </form>
  )
}

function LessonRow({ lesson, onChanged }: { lesson: AdminCourseTreeLesson; onChanged: () => void }) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(lesson.title)
  const [order, setOrder] = useState(String(lesson.order))
  const [published, setPublished] = useState(lesson.published)
  const [contentJson, setContentJson] = useState(JSON.stringify(lesson.content, null, 2))
  const [error, setError] = useState<string | null>(null)

  const updateMutation = useMutation({
    mutationFn: () => {
      const content = JSON.parse(contentJson)
      return adminApi.updateLesson(lesson.id, { title, order: Number(order), published, content })
    },
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Invalid JSON in content.'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteLesson(lesson.id),
    onSuccess: onChanged,
  })

  if (!editing) {
    return (
      <div className="rounded-lg border border-border p-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs text-text-muted">#{lesson.order}</span>
          <span className="flex-1 text-sm font-medium text-text">{lesson.title}</span>
          <Badge tone={lesson.published ? 'success' : 'neutral'}>{lesson.published ? 'Published' : 'Draft'}</Badge>
          <button onClick={() => setEditing(true)} className="text-text-muted hover:text-primary">
            <Pencil className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => deleteMutation.mutate()}
            disabled={deleteMutation.isPending}
            className="text-text-muted hover:text-error"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
        <QuizEditor lesson={lesson} onChanged={onChanged} />
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-primary/40 p-3">
      <div className="flex flex-col gap-2">
        <div className="flex gap-2">
          <div className="flex-1">
            <Input placeholder="Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="w-20">
            <Input type="number" placeholder="Order" required value={order} onChange={(e) => setOrder(e.target.value)} />
          </div>
          <label className="flex items-center gap-1.5 text-xs text-text-muted">
            <input type="checkbox" checked={published} onChange={(e) => setPublished(e.target.checked)} />
            Published
          </label>
        </div>
        <textarea
          value={contentJson}
          onChange={(e) => setContentJson(e.target.value)}
          rows={10}
          className="rounded-lg border border-border bg-surface p-2 font-mono text-xs text-text"
        />
        <div className="flex gap-2">
          <Button size="sm" disabled={updateMutation.isPending} onClick={() => updateMutation.mutate()}>
            Save
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
            Cancel
          </Button>
        </div>
        <ErrorText message={error} />
      </div>
    </div>
  )
}

function NewLessonForm({ moduleId, onCreated }: { moduleId: string; onCreated: () => void }) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [order, setOrder] = useState('1')
  const [error, setError] = useState<string | null>(null)

  const createMutation = useMutation({
    mutationFn: () =>
      adminApi.createLesson(moduleId, { title, order: Number(order), published: false, content: { blocks: [] } }),
    onSuccess: () => {
      setTitle('')
      setOrder('1')
      setOpen(false)
      onCreated()
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Could not create lesson.'),
  })

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
        <Plus className="h-3 w-3" /> Add lesson
      </button>
    )
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        setError(null)
        createMutation.mutate()
      }}
      className="flex gap-2"
    >
      <div className="flex-1">
        <Input placeholder="Lesson title" required value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>
      <div className="w-20">
        <Input type="number" required value={order} onChange={(e) => setOrder(e.target.value)} />
      </div>
      <Button type="submit" size="sm" disabled={createMutation.isPending}>
        Create
      </Button>
      <Button type="button" size="sm" variant="ghost" onClick={() => setOpen(false)}>
        Cancel
      </Button>
      <ErrorText message={error} />
    </form>
  )
}

function ModuleRow({ module: mod, onChanged }: { module: AdminCourseTreeModule; onChanged: () => void }) {
  const [expanded, setExpanded] = useState(true)
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(mod.title)
  const [order, setOrder] = useState(String(mod.order))
  const [error, setError] = useState<string | null>(null)

  const updateMutation = useMutation({
    mutationFn: () => adminApi.updateModule(mod.id, { title, order: Number(order) }),
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : 'Could not update module.'),
  })

  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteModule(mod.id),
    onSuccess: onChanged,
  })

  return (
    <div className="rounded-lg border border-border bg-bg p-3">
      {editing ? (
        <div className="flex gap-2">
          <div className="flex-1">
            <Input value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="w-20">
            <Input type="number" value={order} onChange={(e) => setOrder(e.target.value)} />
          </div>
          <Button size="sm" disabled={updateMutation.isPending} onClick={() => updateMutation.mutate()}>
            Save
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
            Cancel
          </Button>
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <button onClick={() => setExpanded(!expanded)}>
            <ChevronDown className={cn('h-4 w-4 text-text-muted transition-transform', !expanded && '-rotate-90')} />
          </button>
          <span className="font-mono text-xs text-text-muted">#{mod.order}</span>
          <span className="flex-1 text-sm font-semibold text-text">{mod.title}</span>
          <span className="text-xs text-text-muted">{mod.lessons.length} lessons</span>
          <button onClick={() => setEditing(true)} className="text-text-muted hover:text-primary">
            <Pencil className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => deleteMutation.mutate()}
            disabled={deleteMutation.isPending}
            className="text-text-muted hover:text-error"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      )}
      <ErrorText message={error} />

      {expanded && !editing && (
        <div className="mt-3 flex flex-col gap-2 pl-6">
          {mod.lessons
            .slice()
            .sort((a, b) => a.order - b.order)
            .map((lesson) => (
              <LessonRow key={lesson.id} lesson={lesson} onChanged={onChanged} />
            ))}
          <NewLessonForm moduleId={mod.id} onCreated={onChanged} />
        </div>
      )}
    </div>
  )
}

function NewModuleForm({ courseId, onCreated }: { courseId: string; onCreated: () => void }) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [order, setOrder] = useState('1')

  const createMutation = useMutation({
    mutationFn: () => adminApi.createModule(courseId, { title, order: Number(order) }),
    onSuccess: () => {
      setTitle('')
      setOrder('1')
      setOpen(false)
      onCreated()
    },
  })

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
        <Plus className="h-3 w-3" /> Add module
      </button>
    )
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        createMutation.mutate()
      }}
      className="flex gap-2"
    >
      <div className="flex-1">
        <Input placeholder="Module title" required value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>
      <div className="w-20">
        <Input type="number" required value={order} onChange={(e) => setOrder(e.target.value)} />
      </div>
      <Button type="submit" size="sm" disabled={createMutation.isPending}>
        Create
      </Button>
      <Button type="button" size="sm" variant="ghost" onClick={() => setOpen(false)}>
        Cancel
      </Button>
    </form>
  )
}

function CourseCard({ course, onChanged }: { course: AdminCourse; onChanged: () => void }) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(course.title)
  const [description, setDescription] = useState(course.description ?? '')
  const [level, setLevel] = useState(course.level)
  const [hours, setHours] = useState(String(course.estimated_hours ?? ''))
  const [published, setPublished] = useState(course.published)

  const updateMutation = useMutation({
    mutationFn: () =>
      adminApi.updateCourse(course.id, {
        title,
        description,
        level,
        estimated_hours: hours ? Number(hours) : undefined,
        published,
      }),
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteCourse(course.id),
    onSuccess: onChanged,
  })

  return (
    <Card>
      {editing ? (
        <div className="flex flex-col gap-2">
          <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <Input label="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
          <div className="flex gap-2">
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              className="h-10 flex-1 rounded-lg border border-border bg-surface px-3 text-sm text-text"
            >
              {COURSE_LEVELS.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
            <div className="w-28">
              <Input type="number" placeholder="Hours" value={hours} onChange={(e) => setHours(e.target.value)} />
            </div>
            <label className="flex items-center gap-1.5 text-xs text-text-muted">
              <input type="checkbox" checked={published} onChange={(e) => setPublished(e.target.checked)} />
              Published
            </label>
          </div>
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
        <div className="flex items-start gap-2">
          <button onClick={() => setExpanded(!expanded)} className="mt-0.5">
            <ChevronDown className={cn('h-4 w-4 text-text-muted transition-transform', !expanded && '-rotate-90')} />
          </button>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-text">{course.title}</h3>
              <Badge tone="primary">{course.level}</Badge>
              <Badge tone={course.published ? 'success' : 'neutral'}>{course.published ? 'Published' : 'Draft'}</Badge>
            </div>
            {course.description && <p className="mt-1 text-sm text-text-muted">{course.description}</p>}
            <p className="mt-1 text-xs text-text-muted">
              {course.modules.length} modules · {course.modules.reduce((n, m) => n + m.lessons.length, 0)} lessons
            </p>
          </div>
          <button onClick={() => setEditing(true)} className="text-text-muted hover:text-primary">
            <Pencil className="h-4 w-4" />
          </button>
          <button
            onClick={() => deleteMutation.mutate()}
            disabled={deleteMutation.isPending}
            className="text-text-muted hover:text-error"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      )}

      {expanded && !editing && (
        <div className="mt-4 flex flex-col gap-2 border-t border-border pt-4">
          {course.modules
            .slice()
            .sort((a, b) => a.order - b.order)
            .map((mod) => (
              <ModuleRow key={mod.id} module={mod} onChanged={onChanged} />
            ))}
          <NewModuleForm courseId={course.id} onCreated={onChanged} />
        </div>
      )}
    </Card>
  )
}

export function AdminCourseManager() {
  const queryClient = useQueryClient()
  const { data: courses, isLoading } = useQuery({ queryKey: ['admin', 'courses'], queryFn: adminApi.courses })

  function onChanged() {
    queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] })
    queryClient.invalidateQueries({ queryKey: ['courses'] })
    queryClient.invalidateQueries({ queryKey: ['admin', 'stats'] })
  }

  if (isLoading) return <Skeleton className="h-40" />

  return (
    <div className="flex flex-col gap-3">
      {courses?.map((course) => (
        <CourseCard key={course.id} course={course} onChanged={onChanged} />
      ))}
    </div>
  )
}
