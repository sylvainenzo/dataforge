export interface ToolSummary {
  id: string
  name: string
  slug: string
  description: string
  category: string
  mac_supported: boolean
  apple_silicon_supported: boolean
  intel_supported: boolean
  last_verified_at: string
}

export interface ToolDetail extends ToolSummary {
  official_url: string
  docs_url: string | null
  install_method: string
  homebrew_command: string | null
  verification_command: string | null
  common_errors: Record<string, string> | null
  alternatives: string[] | null
}

export interface WizardChecklistItem {
  tool: ToolSummary
  essential: boolean
  reason: string
}

export type Architecture = 'apple_silicon' | 'intel'
export type Experience = 'beginner' | 'intermediate' | 'advanced'
