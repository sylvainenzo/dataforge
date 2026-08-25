import { CheckCircle2 } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Skeleton } from '@/components/ui/Skeleton'
import { ContentBlockView } from '@/features/curriculum/ContentBlockView'
import { QuizCard } from '@/features/curriculum/QuizCard'
import { useCompleteLesson, useLesson } from '@/hooks/useCurriculum'

export function LessonPage() {
  const { slug = '' } = useParams()
  const { data: lesson, isLoading } = useLesson(slug)
  const complete = useCompleteLesson(slug)

  if (isLoading) return <Skeleton className="h-96" />
  if (!lesson) return <p className="text-sm text-text-muted">Lesson not found.</p>

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text">{lesson.title}</h1>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {lesson.skills.map((skill) => (
              <Badge key={skill.id} tone="accent">
                {skill.name}
              </Badge>
            ))}
          </div>
        </div>
        <Button
          size="sm"
          onClick={() => complete.mutate()}
          disabled={complete.isPending || complete.isSuccess}
        >
          {complete.isSuccess ? (
            <>
              <CheckCircle2 className="h-4 w-4" /> Completed
            </>
          ) : (
            'Mark complete'
          )}
        </Button>
      </div>

      <div className="space-y-5">
        {lesson.content.blocks.map((block, i) => (
          <ContentBlockView key={i} block={block} />
        ))}
      </div>

      {lesson.quiz_id && (
        <div className="mt-8">
          <QuizCard quizId={lesson.quiz_id} />
        </div>
      )}
    </div>
  )
}
