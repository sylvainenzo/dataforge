export interface AdminStats {
  user_count: number
  course_count: number
  lesson_count: number
  dataset_count: number
  project_count: number
  quiz_attempt_count: number
  code_execution_count: number
}

export interface AdminUser {
  id: string
  email: string
  is_active: boolean
  created_at: string
  roles: string[]
}

export interface AdminQuizQuestion {
  id: string
  question_text: string
  question_type: string
  options: { choices?: string[] } | null
  correct_answer: { value?: string }
  explanation: string | null
  order: number
  points: number
}

export interface AdminQuiz {
  id: string
  lesson_id: string | null
  title: string
  passing_score: number
  questions: AdminQuizQuestion[]
}

export interface AdminLesson {
  id: string
  module_id: string
  title: string
  slug: string
  order: number
  content: { blocks: unknown[] }
  estimated_minutes: number | null
  published: boolean
}

export interface AdminCourseTreeLesson extends AdminLesson {
  quiz: AdminQuiz | null
}

export interface AdminModule {
  id: string
  course_id: string
  title: string
  slug: string
  order: number
}

export interface AdminCourseTreeModule extends AdminModule {
  lessons: AdminCourseTreeLesson[]
}

export interface AdminCourse {
  id: string
  title: string
  slug: string
  description: string | null
  level: string
  estimated_hours: number | null
  published: boolean
  modules: AdminCourseTreeModule[]
}

export interface AdminResource {
  id: string
  title: string
  provider: string
  level: string
  is_free: boolean
  description: string | null
  url: string
  last_verified_at: string
}

export interface AdminGlossaryTerm {
  id: string
  term: string
  slug: string
  simple_explanation: string
  technical_explanation: string | null
  example: string | null
}

export interface AdminTool {
  id: string
  name: string
  slug: string
  description: string
  category: string
  official_url: string
  docs_url: string | null
  mac_supported: boolean
  apple_silicon_supported: boolean
  intel_supported: boolean
  install_method: string
  homebrew_command: string | null
  verification_command: string | null
  common_errors: Record<string, string> | null
  alternatives: string[] | null
  last_verified_at: string
}

export interface AdminCareerPath {
  id: string
  name: string
  slug: string
  description: string | null
  skill_weights: Record<string, number>
}

export interface AdminInterviewQuestion {
  id: string
  question: string
  category: string
  difficulty: string
  sample_answer: string
  career_path_id: string | null
}

export interface AdminProject {
  id: string
  title: string
  slug: string
  description: string
  difficulty: string
  project_type: string
  dataset_id: string | null
  rubric: Record<string, unknown>
}

export interface AdminProjectSubmission {
  id: string
  project_id: string
  project_title: string
  user_id: string
  user_email: string
  submission_url: string | null
  status: 'submitted' | 'reviewed' | 'passed'
  feedback: string | null
  submitted_at: string
  reviewed_at: string | null
}

export interface AdminDataset {
  id: string
  name: string
  slug: string
  description: string | null
  source: string
  source_url: string
  license: string
  domain: string | null
  difficulty: string
  format: string
}
