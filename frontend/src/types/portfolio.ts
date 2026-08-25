export interface PortfolioSettings {
  bio: string | null
  portfolio_public: boolean
}

export interface PortfolioProject {
  project_title: string
  project_slug: string
  submission_url: string | null
  reviewed_at: string | null
}

export interface PortfolioCertificate {
  course_title: string
  certificate_number: string
  issued_at: string
}

export interface PublicPortfolio {
  user_id: string
  display_name: string
  bio: string | null
  projects: PortfolioProject[]
  certificates: PortfolioCertificate[]
}
