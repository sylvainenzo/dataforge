import { api } from '@/lib/api'
import type {
  CourseDetail,
  CourseSummary,
  LearningPathDetail,
  LearningPathSummary,
  LessonDetail,
  QuizAttemptResult,
  QuizDetail,
} from '@/types/curriculum'

export const curriculumApi = {
  learningPaths: () => api.get<LearningPathSummary[]>('/api/v1/learning-paths'),
  learningPath: (slug: string) => api.get<LearningPathDetail>(`/api/v1/learning-paths/${slug}`),
  courses: () => api.get<CourseSummary[]>('/api/v1/courses'),
  course: (slug: string) => api.get<CourseDetail>(`/api/v1/courses/${slug}`),
  lesson: (slug: string) => api.get<LessonDetail>(`/api/v1/lessons/${slug}`),
  completeLesson: (slug: string) => api.post<void>(`/api/v1/lessons/${slug}/complete`),
  quiz: (id: string) => api.get<QuizDetail>(`/api/v1/quizzes/${id}`),
  submitQuiz: (id: string, answers: Record<string, string>) =>
    api.post<QuizAttemptResult>(`/api/v1/quizzes/${id}/attempts`, { answers }),
}
