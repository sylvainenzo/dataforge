import { useQuery } from '@tanstack/react-query'
import { MessageCircleQuestion } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { careerApi } from '@/services/careerApi'
import type { LearningLevel } from '@/types/career'

const DIFFICULTIES: LearningLevel[] = ['beginner', 'practical', 'technical', 'advanced', 'professional']

const DIFFICULTY_TONE: Record<LearningLevel, 'success' | 'info' | 'primary' | 'warning' | 'error'> = {
  beginner: 'success',
  practical: 'info',
  technical: 'primary',
  advanced: 'warning',
  professional: 'error',
}

export function InterviewQuestionsPage() {
  const [category, setCategory] = useState('')
  const [difficulty, setDifficulty] = useState('')
  const [careerPath, setCareerPath] = useState('')

  const { data: categories } = useQuery({
    queryKey: ['interview-questions', 'categories'],
    queryFn: careerApi.interviewQuestionCategories,
  })
  const { data: careerPaths } = useQuery({ queryKey: ['career-paths'], queryFn: careerApi.list })
  const { data: questions, isLoading } = useQuery({
    queryKey: ['interview-questions', { category, difficulty, careerPath }],
    queryFn: () =>
      careerApi.interviewQuestions({
        category: category || undefined,
        difficulty: difficulty || undefined,
        career_path: careerPath || undefined,
      }),
  })

  const grouped = useMemo(() => {
    const map = new Map<string, typeof questions>()
    for (const q of questions ?? []) {
      const list = map.get(q.category) ?? []
      list.push(q)
      map.set(q.category, list as NonNullable<typeof questions>)
    }
    return Array.from(map.entries())
  }, [questions])

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-1 text-xl font-bold text-text">Interview Question Bank</h1>
      <p className="mb-4 text-sm text-text-muted">
        Practice real interview questions by category and difficulty. Click a question to reveal a sample answer.
      </p>

      <div className="mb-6 flex flex-wrap gap-3">
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-lg border border-border bg-card px-3 py-1.5 text-sm text-text"
        >
          <option value="">All categories</option>
          {categories?.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <select
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          className="rounded-lg border border-border bg-card px-3 py-1.5 text-sm text-text"
        >
          <option value="">All difficulties</option>
          {DIFFICULTIES.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>

        <select
          value={careerPath}
          onChange={(e) => setCareerPath(e.target.value)}
          className="rounded-lg border border-border bg-card px-3 py-1.5 text-sm text-text"
        >
          <option value="">All career paths</option>
          {careerPaths?.map((p) => (
            <option key={p.id} value={p.slug}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <Skeleton className="h-64" />
      ) : !questions || questions.length === 0 ? (
        <EmptyState
          icon={MessageCircleQuestion}
          title="No questions match these filters"
          description="Try clearing a filter to see more questions."
        />
      ) : (
        <div className="flex flex-col gap-6">
          {grouped.map(([cat, qs]) => (
            <Card key={cat}>
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-text-muted">{cat}</h2>
              <div className="divide-y divide-border">
                {qs?.map((q) => (
                  <details key={q.id} className="group py-3 first:pt-0 last:pb-0">
                    <summary className="flex cursor-pointer list-none items-start justify-between gap-3 marker:content-none">
                      <span className="text-sm font-medium text-text">{q.question}</span>
                      <Badge tone={DIFFICULTY_TONE[q.difficulty]} className="shrink-0">
                        {q.difficulty}
                      </Badge>
                    </summary>
                    <p className="mt-2 text-sm text-text-muted">{q.sample_answer}</p>
                  </details>
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
