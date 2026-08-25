import { api } from '@/lib/api'
import type { Flashcard, FlashcardReviewResult, ProgressSummary, SkillRecommendation } from '@/types/progress'

export const progressApi = {
  summary: () => api.get<ProgressSummary>('/api/v1/progress/summary'),
  dueFlashcards: () => api.get<Flashcard[]>('/api/v1/flashcards/due'),
  reviewFlashcard: (id: string, grade: number) =>
    api.post<FlashcardReviewResult>(`/api/v1/flashcards/${id}/review`, { grade }),
  recommendations: () => api.get<SkillRecommendation[]>('/api/v1/progress/recommendations'),
}
