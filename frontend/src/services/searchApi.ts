import { api } from '@/lib/api'
import type { SearchResult } from '@/types/search'

export const searchApi = {
  search: (q: string) => api.get<SearchResult[]>(`/api/v1/search?q=${encodeURIComponent(q)}`),
}
