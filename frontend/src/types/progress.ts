export interface Achievement {
  key: string
  name: string
  description: string
  xp_reward: number
  icon: string | null
}

export interface ProgressSummary {
  xp: number
  streak_days: number
  badges: Achievement[]
  newly_awarded: string[]
}

export interface Flashcard {
  id: string
  front: string
  back: string
}

export interface FlashcardReviewResult {
  interval_days: number
  due_at: string
  repetitions: number
}

export interface SkillRecommendation {
  skill_id: string
  skill_name: string
  skill_slug: string
  lessons_completed: number
  lessons_total: number
  completion: number
  next_lesson: { slug: string; title: string } | null
}
