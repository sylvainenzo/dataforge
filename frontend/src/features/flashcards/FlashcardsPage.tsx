import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { progressApi } from '@/services/progressApi'

const GRADES = [
  { grade: 0, label: 'Again', tone: 'bg-error text-white' },
  { grade: 3, label: 'Hard', tone: 'bg-warning text-white' },
  { grade: 4, label: 'Good', tone: 'bg-primary text-white' },
  { grade: 5, label: 'Easy', tone: 'bg-success text-white' },
]

export function FlashcardsPage() {
  const { data: cards, isLoading, refetch } = useQuery({ queryKey: ['flashcards', 'due'], queryFn: progressApi.dueFlashcards })
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)
  const [reviewedCount, setReviewedCount] = useState(0)

  async function grade(g: number) {
    const card = cards?.[index]
    if (!card) return
    await progressApi.reviewFlashcard(card.id, g)
    setReviewedCount((n) => n + 1)
    setRevealed(false)
    if (cards && index + 1 < cards.length) {
      setIndex((i) => i + 1)
    } else {
      await refetch()
      setIndex(0)
    }
  }

  if (isLoading) return <Skeleton className="h-64" />

  const card = cards?.[index]

  if (!card) {
    return (
      <div className="mx-auto max-w-lg pt-12">
        <EmptyState
          icon={CheckCircle2}
          title={reviewedCount > 0 ? 'All caught up' : 'No cards due right now'}
          description={
            reviewedCount > 0
              ? `Reviewed ${reviewedCount} card${reviewedCount === 1 ? '' : 's'}. Come back when more are due.`
              : 'Flashcards appear here as they become due, based on the SM-2 spaced repetition schedule.'
          }
        />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-lg">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-text">Flashcards</h1>
        <span className="text-sm text-text-muted">
          {index + 1} / {cards.length}
        </span>
      </div>

      <Card className="flex min-h-56 flex-col items-center justify-center gap-4 text-center">
        <Sparkles className="h-5 w-5 text-primary" />
        <p className="text-lg text-text">{card.front}</p>
        {revealed && <p className="border-t border-border pt-4 text-text-muted">{card.back}</p>}
      </Card>

      <div className="mt-4">
        {!revealed ? (
          <Button className="w-full" onClick={() => setRevealed(true)}>
            Show answer
          </Button>
        ) : (
          <div className="grid grid-cols-4 gap-2">
            {GRADES.map((g) => (
              <button
                key={g.grade}
                onClick={() => grade(g.grade)}
                className={`rounded-lg px-2 py-2 text-sm font-medium ${g.tone} hover:opacity-90`}
              >
                {g.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
