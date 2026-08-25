import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronDown, Pencil, Plus, Trash2 } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Skeleton } from '@/components/ui/Skeleton'
import { adminApi } from '@/services/adminApi'
import type { AdminCareerPath, AdminGlossaryTerm, AdminInterviewQuestion, AdminResource, AdminTool } from '@/types/admin'

const LEVELS = ['beginner', 'practical', 'technical', 'advanced', 'professional']

function todayIso(): string {
  return new Date().toISOString().slice(0, 10)
}

// ---- Resources ----

function ResourceRow({ resource, onChanged }: { resource: AdminResource; onChanged: () => void }) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(resource.title)
  const [provider, setProvider] = useState(resource.provider)
  const [url, setUrl] = useState(resource.url)
  const [description, setDescription] = useState(resource.description ?? '')

  const updateMutation = useMutation({
    mutationFn: () => adminApi.updateResource(resource.id, { title, provider, url, description }),
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
  })
  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteResource(resource.id),
    onSuccess: onChanged,
  })

  if (editing) {
    return (
      <div className="flex flex-col gap-2 rounded-lg border border-primary/40 p-3">
        <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <Input placeholder="Provider" value={provider} onChange={(e) => setProvider(e.target.value)} />
        <Input placeholder="URL" value={url} onChange={(e) => setUrl(e.target.value)} />
        <Input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
        <div className="flex gap-2">
          <Button size="sm" disabled={updateMutation.isPending} onClick={() => updateMutation.mutate()}>
            Save
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
            Cancel
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 rounded-lg border border-border p-3">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate text-sm font-medium text-text">{resource.title}</span>
          <Badge tone="primary">{resource.level}</Badge>
          {resource.is_free && <Badge tone="success">Free</Badge>}
        </div>
        <p className="truncate text-xs text-text-muted">
          {resource.provider} · {resource.url}
        </p>
      </div>
      <button onClick={() => setEditing(true)} className="text-text-muted hover:text-primary">
        <Pencil className="h-3.5 w-3.5" />
      </button>
      <button onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending} className="text-text-muted hover:text-error">
        <Trash2 className="h-3.5 w-3.5" />
      </button>
    </div>
  )
}

function NewResourceForm({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [provider, setProvider] = useState('')
  const [url, setUrl] = useState('')
  const [level, setLevel] = useState('beginner')
  const [isFree, setIsFree] = useState(true)

  const createMutation = useMutation({
    mutationFn: () =>
      adminApi.createResource({ title, provider, url, level, is_free: isFree, last_verified_at: todayIso() }),
    onSuccess: () => {
      setTitle('')
      setProvider('')
      setUrl('')
      setOpen(false)
      onCreated()
    },
  })

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
        <Plus className="h-3 w-3" /> Add resource
      </button>
    )
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        createMutation.mutate()
      }}
      className="flex flex-col gap-2 rounded-lg border border-border p-3"
    >
      <Input placeholder="Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
      <Input placeholder="Provider" required value={provider} onChange={(e) => setProvider(e.target.value)} />
      <Input placeholder="URL" required type="url" value={url} onChange={(e) => setUrl(e.target.value)} />
      <div className="flex items-center gap-3">
        <select value={level} onChange={(e) => setLevel(e.target.value)} className="h-10 rounded-lg border border-border bg-surface px-3 text-sm text-text">
          {LEVELS.map((l) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-1.5 text-xs text-text-muted">
          <input type="checkbox" checked={isFree} onChange={(e) => setIsFree(e.target.checked)} />
          Free
        </label>
      </div>
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

function ResourcesSection() {
  const queryClient = useQueryClient()
  const { data: resources, isLoading } = useQuery({ queryKey: ['admin', 'resources'], queryFn: adminApi.resources })

  function onChanged() {
    queryClient.invalidateQueries({ queryKey: ['admin', 'resources'] })
    queryClient.invalidateQueries({ queryKey: ['resources'] })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Resources</CardTitle>
      </CardHeader>
      {isLoading ? (
        <Skeleton className="h-24" />
      ) : (
        <div className="flex flex-col gap-2">
          {resources?.map((r) => (
            <ResourceRow key={r.id} resource={r} onChanged={onChanged} />
          ))}
          <NewResourceForm onCreated={onChanged} />
        </div>
      )}
    </Card>
  )
}

// ---- Glossary ----

function GlossaryRow({ term, onChanged }: { term: AdminGlossaryTerm; onChanged: () => void }) {
  const [editing, setEditing] = useState(false)
  const [simpleExplanation, setSimpleExplanation] = useState(term.simple_explanation)

  const updateMutation = useMutation({
    mutationFn: () => adminApi.updateGlossaryTerm(term.id, { simple_explanation: simpleExplanation }),
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
  })
  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteGlossaryTerm(term.id),
    onSuccess: onChanged,
  })

  return (
    <div className="rounded-lg border border-border p-3">
      <div className="flex items-center gap-2">
        <span className="flex-1 text-sm font-medium text-text">{term.term}</span>
        <button onClick={() => setEditing(!editing)} className="text-text-muted hover:text-primary">
          <Pencil className="h-3.5 w-3.5" />
        </button>
        <button onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending} className="text-text-muted hover:text-error">
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
      {editing ? (
        <div className="mt-2 flex flex-col gap-2">
          <Input value={simpleExplanation} onChange={(e) => setSimpleExplanation(e.target.value)} />
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
        <p className="mt-1 text-xs text-text-muted">{term.simple_explanation}</p>
      )}
    </div>
  )
}

function NewGlossaryTermForm({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false)
  const [term, setTerm] = useState('')
  const [simpleExplanation, setSimpleExplanation] = useState('')

  const createMutation = useMutation({
    mutationFn: () => adminApi.createGlossaryTerm({ term, simple_explanation: simpleExplanation }),
    onSuccess: () => {
      setTerm('')
      setSimpleExplanation('')
      setOpen(false)
      onCreated()
    },
  })

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
        <Plus className="h-3 w-3" /> Add term
      </button>
    )
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        createMutation.mutate()
      }}
      className="flex flex-col gap-2 rounded-lg border border-border p-3"
    >
      <Input placeholder="Term" required value={term} onChange={(e) => setTerm(e.target.value)} />
      <Input
        placeholder="Simple explanation"
        required
        value={simpleExplanation}
        onChange={(e) => setSimpleExplanation(e.target.value)}
      />
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

function GlossarySection() {
  const queryClient = useQueryClient()
  const { data: terms, isLoading } = useQuery({ queryKey: ['admin', 'glossary'], queryFn: adminApi.glossaryTerms })

  function onChanged() {
    queryClient.invalidateQueries({ queryKey: ['admin', 'glossary'] })
    queryClient.invalidateQueries({ queryKey: ['glossary'] })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Glossary</CardTitle>
      </CardHeader>
      {isLoading ? (
        <Skeleton className="h-24" />
      ) : (
        <div className="flex flex-col gap-2">
          {terms?.map((t) => (
            <GlossaryRow key={t.id} term={t} onChanged={onChanged} />
          ))}
          <NewGlossaryTermForm onCreated={onChanged} />
        </div>
      )}
    </Card>
  )
}

// ---- Tools ----

function ToolRow({ tool, onChanged }: { tool: AdminTool; onChanged: () => void }) {
  const [editing, setEditing] = useState(false)
  const [description, setDescription] = useState(tool.description)

  const updateMutation = useMutation({
    mutationFn: () => adminApi.updateTool(tool.id, { description }),
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
  })
  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteTool(tool.id),
    onSuccess: onChanged,
  })

  return (
    <div className="rounded-lg border border-border p-3">
      <div className="flex items-center gap-2">
        <span className="flex-1 text-sm font-medium text-text">{tool.name}</span>
        <Badge tone="neutral">{tool.category}</Badge>
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
        <p className="mt-1 text-xs text-text-muted">{tool.description}</p>
      )}
    </div>
  )
}

function NewToolForm({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('')
  const [officialUrl, setOfficialUrl] = useState('')

  const createMutation = useMutation({
    mutationFn: () =>
      adminApi.createTool({
        name,
        description,
        category,
        official_url: officialUrl,
        mac_supported: true,
        apple_silicon_supported: true,
        intel_supported: true,
        install_method: 'brew',
        last_verified_at: todayIso(),
      }),
    onSuccess: () => {
      setName('')
      setDescription('')
      setCategory('')
      setOfficialUrl('')
      setOpen(false)
      onCreated()
    },
  })

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
        <Plus className="h-3 w-3" /> Add tool
      </button>
    )
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        createMutation.mutate()
      }}
      className="flex flex-col gap-2 rounded-lg border border-border p-3"
    >
      <Input placeholder="Name" required value={name} onChange={(e) => setName(e.target.value)} />
      <Input placeholder="Description" required value={description} onChange={(e) => setDescription(e.target.value)} />
      <Input placeholder="Category" required value={category} onChange={(e) => setCategory(e.target.value)} />
      <Input placeholder="Official URL" required type="url" value={officialUrl} onChange={(e) => setOfficialUrl(e.target.value)} />
      <p className="text-xs text-text-muted">Assumes Mac/Apple Silicon/Intel supported, install via Homebrew — edit after creating if not accurate.</p>
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

function ToolsSection() {
  const queryClient = useQueryClient()
  const { data: tools, isLoading } = useQuery({ queryKey: ['admin', 'tools'], queryFn: adminApi.tools })

  function onChanged() {
    queryClient.invalidateQueries({ queryKey: ['admin', 'tools'] })
    queryClient.invalidateQueries({ queryKey: ['tools'] })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tools</CardTitle>
      </CardHeader>
      {isLoading ? (
        <Skeleton className="h-24" />
      ) : (
        <div className="flex flex-col gap-2">
          {tools?.map((t) => (
            <ToolRow key={t.id} tool={t} onChanged={onChanged} />
          ))}
          <NewToolForm onCreated={onChanged} />
        </div>
      )}
    </Card>
  )
}

// ---- Career paths ----

function CareerPathRow({ careerPath, onChanged }: { careerPath: AdminCareerPath; onChanged: () => void }) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [description, setDescription] = useState(careerPath.description ?? '')
  const [weightsJson, setWeightsJson] = useState(JSON.stringify(careerPath.skill_weights, null, 2))
  const [error, setError] = useState<string | null>(null)

  const updateMutation = useMutation({
    mutationFn: () => {
      const skill_weights = JSON.parse(weightsJson)
      return adminApi.updateCareerPath(careerPath.id, { description, skill_weights })
    },
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
    onError: () => setError('Skill weights must be valid JSON: {"skill-slug": 2.5}'),
  })
  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteCareerPath(careerPath.id),
    onSuccess: onChanged,
  })

  return (
    <div className="rounded-lg border border-border p-3">
      <div className="flex items-center gap-2">
        <button onClick={() => setExpanded(!expanded)}>
          <ChevronDown className={`h-4 w-4 text-text-muted transition-transform ${!expanded ? '-rotate-90' : ''}`} />
        </button>
        <span className="flex-1 text-sm font-medium text-text">{careerPath.name}</span>
        <span className="text-xs text-text-muted">{Object.keys(careerPath.skill_weights).length} skills</span>
        <button onClick={() => setEditing(!editing)} className="text-text-muted hover:text-primary">
          <Pencil className="h-3.5 w-3.5" />
        </button>
        <button onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending} className="text-text-muted hover:text-error">
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
      {editing ? (
        <div className="mt-2 flex flex-col gap-2">
          <Input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
          <textarea
            value={weightsJson}
            onChange={(e) => setWeightsJson(e.target.value)}
            rows={5}
            className="rounded-lg border border-border bg-surface p-2 font-mono text-xs text-text"
          />
          <div className="flex gap-2">
            <Button
              size="sm"
              disabled={updateMutation.isPending}
              onClick={() => {
                setError(null)
                try {
                  JSON.parse(weightsJson)
                } catch {
                  setError('Skill weights must be valid JSON.')
                  return
                }
                updateMutation.mutate()
              }}
            >
              Save
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
              Cancel
            </Button>
          </div>
          {error && <p className="text-xs text-error">{error}</p>}
        </div>
      ) : (
        expanded && (
          <div className="mt-2 space-y-1 text-xs text-text-muted">
            {careerPath.description && <p>{careerPath.description}</p>}
            {Object.entries(careerPath.skill_weights).map(([slug, weight]) => (
              <div key={slug} className="flex justify-between">
                <span>{slug}</span>
                <span className="font-mono">{weight}×</span>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  )
}

function NewCareerPathForm({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [weightsJson, setWeightsJson] = useState('{\n  "python-fundamentals": 2.0\n}')
  const [error, setError] = useState<string | null>(null)

  const createMutation = useMutation({
    mutationFn: () => {
      const skill_weights = JSON.parse(weightsJson)
      return adminApi.createCareerPath({ name, description, skill_weights })
    },
    onSuccess: () => {
      setName('')
      setDescription('')
      setOpen(false)
      onCreated()
    },
    onError: () => setError('Could not create — check the JSON is valid and skill slugs exist.'),
  })

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
        <Plus className="h-3 w-3" /> Add career path
      </button>
    )
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      JSON.parse(weightsJson)
    } catch {
      setError('Skill weights must be valid JSON.')
      return
    }
    createMutation.mutate()
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-2 rounded-lg border border-border p-3">
      <Input placeholder="Name" required value={name} onChange={(e) => setName(e.target.value)} />
      <Input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
      <textarea
        value={weightsJson}
        onChange={(e) => setWeightsJson(e.target.value)}
        rows={4}
        className="rounded-lg border border-border bg-surface p-2 font-mono text-xs text-text"
      />
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={createMutation.isPending}>
          Create
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={() => setOpen(false)}>
          Cancel
        </Button>
      </div>
      {error && <p className="text-xs text-error">{error}</p>}
    </form>
  )
}

function CareerPathsSection() {
  const queryClient = useQueryClient()
  const { data: careerPaths, isLoading } = useQuery({ queryKey: ['admin', 'career-paths'], queryFn: adminApi.careerPaths })

  function onChanged() {
    queryClient.invalidateQueries({ queryKey: ['admin', 'career-paths'] })
    queryClient.invalidateQueries({ queryKey: ['career-paths'] })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Career Paths</CardTitle>
      </CardHeader>
      {isLoading ? (
        <Skeleton className="h-24" />
      ) : (
        <div className="flex flex-col gap-2">
          {careerPaths?.map((cp) => (
            <CareerPathRow key={cp.id} careerPath={cp} onChanged={onChanged} />
          ))}
          <NewCareerPathForm onCreated={onChanged} />
        </div>
      )}
    </Card>
  )
}

// ---- Interview questions ----

function InterviewQuestionRow({
  question,
  careerPaths,
  onChanged,
}: {
  question: AdminInterviewQuestion
  careerPaths: AdminCareerPath[]
  onChanged: () => void
}) {
  const [editing, setEditing] = useState(false)
  const [questionText, setQuestionText] = useState(question.question)
  const [category, setCategory] = useState(question.category)
  const [difficulty, setDifficulty] = useState(question.difficulty)
  const [sampleAnswer, setSampleAnswer] = useState(question.sample_answer)
  const [careerPathId, setCareerPathId] = useState(question.career_path_id ?? '')

  const updateMutation = useMutation({
    mutationFn: () =>
      adminApi.updateInterviewQuestion(question.id, {
        question: questionText,
        category,
        difficulty,
        sample_answer: sampleAnswer,
        career_path_id: careerPathId || null,
      }),
    onSuccess: () => {
      setEditing(false)
      onChanged()
    },
  })
  const deleteMutation = useMutation({
    mutationFn: () => adminApi.deleteInterviewQuestion(question.id),
    onSuccess: onChanged,
  })

  if (editing) {
    return (
      <div className="flex flex-col gap-2 rounded-lg border border-primary/40 p-3">
        <Input placeholder="Question" value={questionText} onChange={(e) => setQuestionText(e.target.value)} />
        <Input placeholder="Category" value={category} onChange={(e) => setCategory(e.target.value)} />
        <textarea
          placeholder="Sample answer"
          value={sampleAnswer}
          onChange={(e) => setSampleAnswer(e.target.value)}
          rows={3}
          className="rounded-lg border border-border bg-surface p-2 text-sm text-text"
        />
        <div className="flex items-center gap-3">
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="h-10 rounded-lg border border-border bg-surface px-3 text-sm text-text"
          >
            {LEVELS.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
          <select
            value={careerPathId}
            onChange={(e) => setCareerPathId(e.target.value)}
            className="h-10 rounded-lg border border-border bg-surface px-3 text-sm text-text"
          >
            <option value="">No career path</option>
            {careerPaths.map((cp) => (
              <option key={cp.id} value={cp.id}>
                {cp.name}
              </option>
            ))}
          </select>
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
    )
  }

  return (
    <div className="rounded-lg border border-border p-3">
      <div className="flex items-start gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-text">{question.question}</span>
            <Badge tone="neutral">{question.category}</Badge>
            <Badge tone="primary">{question.difficulty}</Badge>
          </div>
          <p className="mt-1 text-xs text-text-muted">{question.sample_answer}</p>
        </div>
        <button onClick={() => setEditing(true)} className="text-text-muted hover:text-primary">
          <Pencil className="h-3.5 w-3.5" />
        </button>
        <button onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending} className="text-text-muted hover:text-error">
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  )
}

function NewInterviewQuestionForm({
  careerPaths,
  onCreated,
}: {
  careerPaths: AdminCareerPath[]
  onCreated: () => void
}) {
  const [open, setOpen] = useState(false)
  const [questionText, setQuestionText] = useState('')
  const [category, setCategory] = useState('')
  const [difficulty, setDifficulty] = useState('practical')
  const [sampleAnswer, setSampleAnswer] = useState('')
  const [careerPathId, setCareerPathId] = useState('')

  const createMutation = useMutation({
    mutationFn: () =>
      adminApi.createInterviewQuestion({
        question: questionText,
        category,
        difficulty,
        sample_answer: sampleAnswer,
        career_path_id: careerPathId || null,
      }),
    onSuccess: () => {
      setQuestionText('')
      setCategory('')
      setSampleAnswer('')
      setCareerPathId('')
      setOpen(false)
      onCreated()
    },
  })

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
        <Plus className="h-3 w-3" /> Add interview question
      </button>
    )
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        createMutation.mutate()
      }}
      className="flex flex-col gap-2 rounded-lg border border-border p-3"
    >
      <Input placeholder="Question" required value={questionText} onChange={(e) => setQuestionText(e.target.value)} />
      <Input placeholder="Category (e.g. SQL, Behavioral)" required value={category} onChange={(e) => setCategory(e.target.value)} />
      <textarea
        placeholder="Sample answer"
        required
        value={sampleAnswer}
        onChange={(e) => setSampleAnswer(e.target.value)}
        rows={3}
        className="rounded-lg border border-border bg-surface p-2 text-sm text-text"
      />
      <div className="flex items-center gap-3">
        <select
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          className="h-10 rounded-lg border border-border bg-surface px-3 text-sm text-text"
        >
          {LEVELS.map((l) => (
            <option key={l} value={l}>
              {l}
            </option>
          ))}
        </select>
        <select
          value={careerPathId}
          onChange={(e) => setCareerPathId(e.target.value)}
          className="h-10 rounded-lg border border-border bg-surface px-3 text-sm text-text"
        >
          <option value="">No career path</option>
          {careerPaths.map((cp) => (
            <option key={cp.id} value={cp.id}>
              {cp.name}
            </option>
          ))}
        </select>
      </div>
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

function InterviewQuestionsSection() {
  const queryClient = useQueryClient()
  const { data: questions, isLoading } = useQuery({
    queryKey: ['admin', 'interview-questions'],
    queryFn: adminApi.interviewQuestions,
  })
  const { data: careerPaths } = useQuery({ queryKey: ['admin', 'career-paths'], queryFn: adminApi.careerPaths })

  function onChanged() {
    queryClient.invalidateQueries({ queryKey: ['admin', 'interview-questions'] })
    queryClient.invalidateQueries({ queryKey: ['interview-questions'] })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Interview Questions</CardTitle>
      </CardHeader>
      {isLoading ? (
        <Skeleton className="h-24" />
      ) : (
        <div className="flex flex-col gap-2">
          {questions?.map((q) => (
            <InterviewQuestionRow key={q.id} question={q} careerPaths={careerPaths ?? []} onChanged={onChanged} />
          ))}
          <NewInterviewQuestionForm careerPaths={careerPaths ?? []} onCreated={onChanged} />
        </div>
      )}
    </Card>
  )
}

export function AdminKnowledgeCareerManager() {
  return (
    <div className="flex flex-col gap-4">
      <ResourcesSection />
      <GlossarySection />
      <ToolsSection />
      <CareerPathsSection />
      <InterviewQuestionsSection />
    </div>
  )
}
