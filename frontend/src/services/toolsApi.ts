import { api } from '@/lib/api'
import type { Architecture, Experience, ToolDetail, ToolSummary, WizardChecklistItem } from '@/types/tools'

export const toolsApi = {
  list: () => api.get<ToolSummary[]>('/api/v1/tools'),
  detail: (slug: string) => api.get<ToolDetail>(`/api/v1/tools/${slug}`),
  checklist: (architecture: Architecture, career: string, experience: Experience) =>
    api.post<WizardChecklistItem[]>('/api/v1/mac-setup/checklist', { architecture, career, experience }),
}
