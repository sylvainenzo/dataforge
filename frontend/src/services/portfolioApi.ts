import { api } from '@/lib/api'
import type { PortfolioSettings, PublicPortfolio } from '@/types/portfolio'

export const portfolioApi = {
  settings: () => api.get<PortfolioSettings>('/api/v1/portfolio/settings'),
  updateSettings: (payload: Partial<PortfolioSettings>) =>
    api.patch<PortfolioSettings>('/api/v1/portfolio/settings', payload),
  public: (userId: string) => api.get<PublicPortfolio>(`/api/v1/portfolio/${userId}`),
}
