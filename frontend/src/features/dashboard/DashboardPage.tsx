import { useQuery } from '@tanstack/react-query'
import { ArrowRight, BookOpen, Clock, Database, Flame, FlaskConical, Sparkles, Target, Trophy } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { Skeleton } from '@/components/ui/Skeleton'
import { useCurrentUser } from '@/hooks/useAuth'
import { useCourses } from '@/hooks/useCurriculum'
import { progressApi } from '@/services/progressApi'

export function DashboardPage() {
  const { user } = useCurrentUser()
  const { data: courses, isLoading: coursesLoading } = useCourses()
  const { data: progress, isLoading: progressLoading } = useQuery({
    queryKey: ['progress', 'summary'],
    queryFn: progressApi.summary,
  })
  const { data: recommendations, isLoading: recommendationsLoading } = useQuery({
    queryKey: ['progress', 'recommendations'],
    queryFn: progressApi.recommendations,
  })
  const { t } = useTranslation()

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <div>
        <h1 className="text-xl font-bold text-text">
          {t('dashboard.welcome')}{user ? `, ${user.display_name ?? user.email.split('@')[0]}` : ''}
        </h1>
        <div className="mt-2 flex items-center gap-2">
          {user?.roles.map((role) => (
            <Badge key={role} tone="primary">
              {role}
            </Badge>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-soft">
            <Trophy className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="font-mono text-lg font-bold text-text">{progressLoading ? '—' : progress?.xp}</p>
            <p className="text-xs text-text-muted">{t('dashboard.xpEarned')}</p>
          </div>
        </Card>
        <Card className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-warning-soft">
            <Flame className="h-5 w-5 text-warning" />
          </div>
          <div>
            <p className="font-mono text-lg font-bold text-text">{progressLoading ? '—' : progress?.streak_days}</p>
            <p className="text-xs text-text-muted">{t('dashboard.dayStreak')}</p>
          </div>
        </Card>
        <Card className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent-soft">
            <Sparkles className="h-5 w-5 text-accent" />
          </div>
          <div>
            <p className="font-mono text-lg font-bold text-text">{progressLoading ? '—' : progress?.badges.length}</p>
            <p className="text-xs text-text-muted">{t('dashboard.badgesEarned')}</p>
          </div>
        </Card>
      </div>

      {progress && progress.badges.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t('dashboard.yourBadges')}</CardTitle>
          </CardHeader>
          <div className="flex flex-wrap gap-2">
            {progress.badges.map((b) => (
              <Badge key={b.key} tone="primary">
                {b.name}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {recommendationsLoading ? (
        <Skeleton className="h-32" />
      ) : (
        recommendations &&
        recommendations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Recommended for you</CardTitle>
              <Target className="h-4 w-4 text-text-muted" />
            </CardHeader>
            <div className="space-y-3">
              {recommendations.map((r) => (
                <div key={r.skill_id}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="font-medium text-text">{r.skill_name}</span>
                    <span className="font-mono text-xs text-text-muted">
                      {r.lessons_completed}/{r.lessons_total} lessons
                    </span>
                  </div>
                  <ProgressBar value={r.completion * 100} />
                  {r.next_lesson && (
                    <Link
                      to={`/lessons/${r.next_lesson.slug}`}
                      className="mt-1.5 flex items-center gap-1 text-xs text-primary hover:underline"
                    >
                      Continue: {r.next_lesson.title} <ArrowRight className="h-3 w-3" />
                    </Link>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t('dashboard.courses')}</CardTitle>
            <BookOpen className="h-4 w-4 text-text-muted" />
          </CardHeader>
          {coursesLoading ? (
            <Skeleton className="h-24" />
          ) : courses && courses.length > 0 ? (
            <div className="space-y-2">
              {courses.slice(0, 3).map((course) => (
                <Link
                  key={course.id}
                  to={`/courses/${course.slug}`}
                  className="flex items-center justify-between rounded-lg border border-border px-3 py-2.5 text-sm transition-colors hover:bg-surface"
                >
                  <div>
                    <p className="font-medium text-text">{course.title}</p>
                    {course.estimated_hours && (
                      <p className="flex items-center gap-1 text-xs text-text-muted">
                        <Clock className="h-3 w-3" /> {course.estimated_hours}h
                      </p>
                    )}
                  </div>
                  <ArrowRight className="h-4 w-4 text-text-muted" />
                </Link>
              ))}
            </div>
          ) : (
            <EmptyState icon={BookOpen} title="No published courses yet" description="Check back once the curriculum team publishes something." />
          )}
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('dashboard.labs')}</CardTitle>
            <FlaskConical className="h-4 w-4 text-text-muted" />
          </CardHeader>
          <div className="space-y-2">
            <Link to="/labs" className="flex items-center justify-between rounded-lg border border-border px-3 py-2.5 text-sm transition-colors hover:bg-surface">
              <span className="font-medium text-text">Python, SQL, R, Statistics, Data Viz</span>
              <ArrowRight className="h-4 w-4 text-text-muted" />
            </Link>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('dashboard.flashcards')}</CardTitle>
            <Sparkles className="h-4 w-4 text-text-muted" />
          </CardHeader>
          <Link to="/flashcards" className="flex items-center justify-between rounded-lg border border-border px-3 py-2.5 text-sm transition-colors hover:bg-surface">
            <span className="font-medium text-text">{t('dashboard.reviewDueCards')}</span>
            <ArrowRight className="h-4 w-4 text-text-muted" />
          </Link>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('dashboard.datasets')}</CardTitle>
            <Database className="h-4 w-4 text-text-muted" />
          </CardHeader>
          <Link to="/datasets" className="flex items-center justify-between rounded-lg border border-border px-3 py-2.5 text-sm transition-colors hover:bg-surface">
            <span className="font-medium text-text">{t('dashboard.uploadAndExplore')}</span>
            <ArrowRight className="h-4 w-4 text-text-muted" />
          </Link>
        </Card>
      </div>
    </div>
  )
}
