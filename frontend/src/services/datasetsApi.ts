import { ApiError, api } from '@/lib/api'
import type { DatasetDetail, DatasetSummary } from '@/types/datasets'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const datasetsApi = {
  list: () => api.get<DatasetSummary[]>('/api/v1/datasets'),
  detail: (slug: string) => api.get<DatasetDetail>(`/api/v1/datasets/${slug}`),
  upload: async (file: File, name: string, description: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    formData.append('description', description)

    const response = await fetch(`${API_BASE_URL}/api/v1/datasets/upload`, {
      method: 'POST',
      credentials: 'include',
      body: formData,
    })
    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: response.statusText }))
      throw new ApiError(response.status, body.detail ?? 'Upload failed')
    }
    return response.json() as Promise<DatasetSummary>
  },
}
