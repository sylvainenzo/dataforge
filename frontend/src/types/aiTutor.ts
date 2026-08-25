export type TutorMode =
  | 'explain'
  | 'hint'
  | 'debug'
  | 'quiz_me'
  | 'interview_me'
  | 'review_code'
  | 'review_analysis'
  | 'explain_graph'
  | 'explain_error'
  | 'give_project'
  | 'create_practice'

export interface CreateSessionPayload {
  mode: TutorMode
  lesson_title?: string
  code?: string
  error_message?: string
  skill_level?: string
}

export interface TutorSession {
  id: string
  mode: TutorMode
  started_at: string
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}
