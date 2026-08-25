import { api } from '@/lib/api'
import type { ProjectDetail, ProjectSubmission, ProjectSummary } from '@/types/projects'

export const projectsApi = {
  list: () => api.get<ProjectSummary[]>('/api/v1/projects'),
  detail: (slug: string) => api.get<ProjectDetail>(`/api/v1/projects/${slug}`),
  submit: (slug: string, submission_url: string) =>
    api.post<ProjectSubmission>(`/api/v1/projects/${slug}/submissions`, { submission_url }),
  mySubmissions: (slug: string) => api.get<ProjectSubmission[]>(`/api/v1/projects/${slug}/submissions`),
}
