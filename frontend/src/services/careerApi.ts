import { api } from '@/lib/api'
import type { CareerPathDetail, CareerPathProgress, CareerPathSummary, InterviewQuestion } from '@/types/career'

export interface InterviewQuestionFilters {
  category?: string
  difficulty?: string
  career_path?: string
}

export const careerApi = {
  list: () => api.get<CareerPathSummary[]>('/api/v1/career-paths'),
  detail: (slug: string) => api.get<CareerPathDetail>(`/api/v1/career-paths/${slug}`),
  progress: (slug: string) => api.get<CareerPathProgress>(`/api/v1/career-paths/${slug}/progress`),
  interviewQuestions: (filters: InterviewQuestionFilters = {}) => {
    const params = new URLSearchParams()
    if (filters.category) params.set('category', filters.category)
    if (filters.difficulty) params.set('difficulty', filters.difficulty)
    if (filters.career_path) params.set('career_path', filters.career_path)
    const query = params.toString()
    return api.get<InterviewQuestion[]>(`/api/v1/interview-questions${query ? `?${query}` : ''}`)
  },
  interviewQuestionCategories: () => api.get<string[]>('/api/v1/interview-questions/categories'),
}
