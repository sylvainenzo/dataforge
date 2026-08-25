import { api } from '@/lib/api'
import type { CreateSessionPayload, TutorSession } from '@/types/aiTutor'

export const aiTutorApi = {
  createSession: (payload: CreateSessionPayload) => api.post<TutorSession>('/api/v1/ai-tutor/sessions', payload),
}
