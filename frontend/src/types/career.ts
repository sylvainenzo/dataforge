export interface CareerPathSummary {
  id: string
  name: string
  slug: string
  description: string | null
}

export interface CareerPathSkill {
  skill_id: string
  skill_name: string
  skill_slug: string
  weight: number
}

export interface CareerPathDetail extends CareerPathSummary {
  skills: CareerPathSkill[]
}

export interface SkillProgress {
  skill_id: string
  skill_name: string
  skill_slug: string
  weight: number
  lessons_completed: number
  lessons_total: number
  completion: number
}

export interface CareerPathProgress {
  career_path_id: string
  career_path_name: string
  overall_completion: number
  skills: SkillProgress[]
}

export type LearningLevel = 'beginner' | 'practical' | 'technical' | 'advanced' | 'professional'

export interface InterviewQuestion {
  id: string
  question: string
  category: string
  difficulty: LearningLevel
  sample_answer: string
  career_path_id: string | null
}
