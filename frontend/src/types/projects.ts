export interface ProjectSummary {
  id: string
  title: string
  slug: string
  description: string
  difficulty: string
  project_type: string
}

export interface ProjectRubric {
  business_problem: string
  objectives: string[]
  questions: string[]
  skills: string[]
  tools: string[]
  steps: string[]
  deliverables: string[]
  evaluation_rubric: Record<string, string>
}

export interface ProjectDetail extends ProjectSummary {
  rubric: ProjectRubric
}

export interface ProjectSubmission {
  id: string
  project_id: string
  submission_url: string | null
  status: 'submitted' | 'reviewed' | 'passed'
  feedback: string | null
  submitted_at: string
  reviewed_at: string | null
}
