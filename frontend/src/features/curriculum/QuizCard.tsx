import { useState } from 'react'
import { CheckCircle2, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useQuiz, useSubmitQuiz } from '@/hooks/useCurriculum'

export function QuizCard({ quizId }: { quizId: string }) {
  const { data: quiz, isLoading } = useQuiz(quizId)
  const submit = useSubmitQuiz(quizId)
  const [answers, setAnswers] = useState<Record<string, string>>({})

  if (isLoading || !quiz) return null

  const allAnswered = quiz.questions.every((q) => answers[q.id])

  return (
    <Card className="border-primary/30">
      <h3 className="mb-4 text-sm font-semibold text-text">{quiz.title}</h3>

      {submit.data ? (
        <div className="flex items-center gap-3 rounded-lg bg-surface p-4">
          {submit.data.passed ? (
            <CheckCircle2 className="h-8 w-8 shrink-0 text-success" />
          ) : (
            <XCircle className="h-8 w-8 shrink-0 text-error" />
          )}
          <div>
            <p className="text-sm font-semibold text-text">
              {submit.data.passed ? 'Passed' : 'Not quite'} — {submit.data.correct_count}/{submit.data.total_questions}{' '}
              correct ({submit.data.score}%)
            </p>
            <p className="text-xs text-text-muted">Passing score: {quiz.passing_score}%</p>
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          {quiz.questions.map((q, i) => (
            <div key={q.id}>
              <p className="mb-2 text-sm text-text">
                {i + 1}. {q.question_text}
              </p>
              <div className="space-y-1.5">
                {q.options?.choices?.map((choice) => (
                  <label
                    key={choice}
                    className="flex cursor-pointer items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm text-text hover:bg-surface has-[:checked]:border-primary has-[:checked]:bg-primary-soft"
                  >
                    <input
                      type="radio"
                      name={q.id}
                      value={choice}
                      checked={answers[q.id] === choice}
                      onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: choice }))}
                      className="accent-[var(--df-primary)]"
                    />
                    {choice}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <Button
            disabled={!allAnswered || submit.isPending}
            onClick={() => submit.mutate(answers)}
          >
            {submit.isPending ? 'Grading…' : 'Submit answers'}
          </Button>
        </div>
      )}
    </Card>
  )
}
