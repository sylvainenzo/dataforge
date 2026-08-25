import { api } from '@/lib/api'
import type { GlossaryTerm, Resource } from '@/types/knowledgeBase'

export const knowledgeBaseApi = {
  resources: () => api.get<Resource[]>('/api/v1/resources'),
  glossary: () => api.get<GlossaryTerm[]>('/api/v1/glossary'),
}
