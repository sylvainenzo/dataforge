export interface LearningPathSummary {
  id: string
  title: string
  slug: string
  description: string | null
}

export interface CourseSummary {
  id: string
  title: string
  slug: string
  description: string | null
  level: string
  estimated_hours: number | null
}

export interface LearningPathDetail extends LearningPathSummary {
  courses: CourseSummary[]
}

export interface LessonSummary {
  id: string
  title: string
  slug: string
  order: number
  estimated_minutes: number | null
}

export interface ModuleWithLessons {
  id: string
  title: string
  slug: string
  order: number
  lessons: LessonSummary[]
}

export interface CourseDetail extends CourseSummary {
  modules: ModuleWithLessons[]
  completed_lesson_ids: string[]
}

export interface Skill {
  id: string
  name: string
  slug: string
  category: string | null
}

export type ContentBlock =
  | { type: 'objectives'; items: string[] }
  | { type: 'explanation'; beginner: string; technical: string }
  | { type: 'code'; language: string; code: string; output?: string }
  | { type: 'exercise'; prompt: string; starter_code: string }
  | { type: 'common_mistakes'; items: string[] }
  | { type: 'summary'; text: string }
  | { type: 'key_terms'; items: string[] }

export interface LessonDetail {
  id: string
  title: string
  slug: string
  order: number
  content: { blocks: ContentBlock[] }
  estimated_minutes: number | null
  skills: Skill[]
  quiz_id: string | null
}

export interface QuizQuestionPublic {
  id: string
  question_text: string
  question_type: string
  options: { choices?: string[] } | null
  order: number
  points: number
}

export interface QuizDetail {
  id: string
  title: string
  passing_score: number
  questions: QuizQuestionPublic[]
}

export interface QuizAttemptResult {
  score: number
  passed: boolean
  correct_count: number
  total_questions: number
}
