export interface Resource {
  id: string
  title: string
  provider: string
  level: string
  is_free: boolean
  description: string | null
  url: string
  last_verified_at: string
}

export interface GlossaryTerm {
  id: string
  term: string
  slug: string
  simple_explanation: string
  technical_explanation: string | null
  example: string | null
}
