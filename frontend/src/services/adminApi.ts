import { api } from '@/lib/api'
import type {
  AdminCareerPath,
  AdminCourse,
  AdminDataset,
  AdminGlossaryTerm,
  AdminInterviewQuestion,
  AdminLesson,
  AdminModule,
  AdminProject,
  AdminProjectSubmission,
  AdminQuiz,
  AdminQuizQuestion,
  AdminResource,
  AdminStats,
  AdminTool,
  AdminUser,
} from '@/types/admin'
import type { CourseSummary } from '@/types/curriculum'

export interface QuizQuestionInput {
  question_text: string
  question_type?: string
  options?: { choices?: string[] } | null
  correct_answer: { value?: string }
  explanation?: string | null
  order: number
  points?: number
}

export const adminApi = {
  stats: () => api.get<AdminStats>('/api/v1/admin/stats'),
  users: () => api.get<AdminUser[]>('/api/v1/admin/users'),
  setUserRole: (userId: string, role: string, grant: boolean) =>
    api.patch<void>(`/api/v1/admin/users/${userId}/role`, { role, grant }),

  courses: () => api.get<AdminCourse[]>('/api/v1/admin/courses'),
  createCourse: (payload: { title: string; description?: string; level: string; estimated_hours?: number; published: boolean }) =>
    api.post<CourseSummary>('/api/v1/admin/courses', payload),
  updateCourse: (
    courseId: string,
    payload: Partial<{ title: string; description: string; level: string; estimated_hours: number; published: boolean }>,
  ) => api.patch<AdminCourse>(`/api/v1/admin/courses/${courseId}`, payload),
  deleteCourse: (courseId: string) => api.delete<void>(`/api/v1/admin/courses/${courseId}`),

  createModule: (courseId: string, payload: { title: string; order: number }) =>
    api.post<AdminModule>(`/api/v1/admin/courses/${courseId}/modules`, payload),
  updateModule: (moduleId: string, payload: Partial<{ title: string; order: number }>) =>
    api.patch<AdminModule>(`/api/v1/admin/modules/${moduleId}`, payload),
  deleteModule: (moduleId: string) => api.delete<void>(`/api/v1/admin/modules/${moduleId}`),

  createLesson: (
    moduleId: string,
    payload: { title: string; order: number; content: { blocks: unknown[] }; estimated_minutes?: number; published: boolean },
  ) => api.post<AdminLesson>(`/api/v1/admin/modules/${moduleId}/lessons`, payload),
  updateLesson: (
    lessonId: string,
    payload: Partial<{
      title: string
      order: number
      content: { blocks: unknown[] }
      estimated_minutes: number
      published: boolean
    }>,
  ) => api.patch<AdminLesson>(`/api/v1/admin/lessons/${lessonId}`, payload),
  deleteLesson: (lessonId: string) => api.delete<void>(`/api/v1/admin/lessons/${lessonId}`),

  createQuiz: (lessonId: string, payload: { title: string; passing_score: number; questions: QuizQuestionInput[] }) =>
    api.post<AdminQuiz>(`/api/v1/admin/lessons/${lessonId}/quiz`, payload),
  updateQuiz: (
    quizId: string,
    payload: Partial<{ title: string; passing_score: number; questions: QuizQuestionInput[] }>,
  ) => api.patch<AdminQuiz>(`/api/v1/admin/quizzes/${quizId}`, payload),
  deleteQuiz: (quizId: string) => api.delete<void>(`/api/v1/admin/quizzes/${quizId}`),

  resources: () => api.get<AdminResource[]>('/api/v1/admin/resources'),
  createResource: (payload: {
    title: string
    provider: string
    level: string
    is_free: boolean
    description?: string
    url: string
    last_verified_at: string
  }) => api.post<AdminResource>('/api/v1/admin/resources', payload),
  updateResource: (resourceId: string, payload: Partial<AdminResource>) =>
    api.patch<AdminResource>(`/api/v1/admin/resources/${resourceId}`, payload),
  deleteResource: (resourceId: string) => api.delete<void>(`/api/v1/admin/resources/${resourceId}`),

  glossaryTerms: () => api.get<AdminGlossaryTerm[]>('/api/v1/admin/glossary'),
  createGlossaryTerm: (payload: { term: string; simple_explanation: string; technical_explanation?: string; example?: string }) =>
    api.post<AdminGlossaryTerm>('/api/v1/admin/glossary', payload),
  updateGlossaryTerm: (termId: string, payload: Partial<AdminGlossaryTerm>) =>
    api.patch<AdminGlossaryTerm>(`/api/v1/admin/glossary/${termId}`, payload),
  deleteGlossaryTerm: (termId: string) => api.delete<void>(`/api/v1/admin/glossary/${termId}`),

  tools: () => api.get<AdminTool[]>('/api/v1/admin/tools'),
  createTool: (payload: {
    name: string
    description: string
    category: string
    official_url: string
    docs_url?: string
    mac_supported: boolean
    apple_silicon_supported: boolean
    intel_supported: boolean
    install_method: string
    homebrew_command?: string
    verification_command?: string
    last_verified_at: string
  }) => api.post<AdminTool>('/api/v1/admin/tools', payload),
  updateTool: (toolId: string, payload: Partial<AdminTool>) => api.patch<AdminTool>(`/api/v1/admin/tools/${toolId}`, payload),
  deleteTool: (toolId: string) => api.delete<void>(`/api/v1/admin/tools/${toolId}`),

  careerPaths: () => api.get<AdminCareerPath[]>('/api/v1/admin/career-paths'),
  createCareerPath: (payload: { name: string; description?: string; skill_weights: Record<string, number> }) =>
    api.post<AdminCareerPath>('/api/v1/admin/career-paths', payload),
  updateCareerPath: (
    careerPathId: string,
    payload: Partial<{ name: string; description: string; skill_weights: Record<string, number> }>,
  ) => api.patch<AdminCareerPath>(`/api/v1/admin/career-paths/${careerPathId}`, payload),
  deleteCareerPath: (careerPathId: string) => api.delete<void>(`/api/v1/admin/career-paths/${careerPathId}`),

  interviewQuestions: () => api.get<AdminInterviewQuestion[]>('/api/v1/admin/interview-questions'),
  createInterviewQuestion: (payload: {
    question: string
    category: string
    difficulty: string
    sample_answer: string
    career_path_id?: string | null
  }) => api.post<AdminInterviewQuestion>('/api/v1/admin/interview-questions', payload),
  updateInterviewQuestion: (
    questionId: string,
    payload: Partial<{
      question: string
      category: string
      difficulty: string
      sample_answer: string
      career_path_id: string | null
    }>,
  ) => api.patch<AdminInterviewQuestion>(`/api/v1/admin/interview-questions/${questionId}`, payload),
  deleteInterviewQuestion: (questionId: string) =>
    api.delete<void>(`/api/v1/admin/interview-questions/${questionId}`),

  projects: () => api.get<AdminProject[]>('/api/v1/admin/projects'),
  createProject: (payload: {
    title: string
    description: string
    difficulty: string
    project_type: string
    dataset_id?: string
    rubric?: Record<string, unknown>
  }) => api.post<AdminProject>('/api/v1/admin/projects', payload),
  updateProject: (
    projectId: string,
    payload: Partial<{ title: string; description: string; difficulty: string; project_type: string; rubric: Record<string, unknown> }>,
  ) => api.patch<AdminProject>(`/api/v1/admin/projects/${projectId}`, payload),
  deleteProject: (projectId: string) => api.delete<void>(`/api/v1/admin/projects/${projectId}`),

  submissions: () => api.get<AdminProjectSubmission[]>('/api/v1/admin/project-submissions'),
  reviewSubmission: (submissionId: string, payload: { status: string; feedback?: string }) =>
    api.patch<AdminProjectSubmission>(`/api/v1/admin/project-submissions/${submissionId}`, payload),

  datasets: () => api.get<AdminDataset[]>('/api/v1/admin/datasets'),
  updateDataset: (
    datasetId: string,
    payload: Partial<{ name: string; description: string; domain: string; difficulty: string }>,
  ) => api.patch<AdminDataset>(`/api/v1/admin/datasets/${datasetId}`, payload),
  deleteDataset: (datasetId: string) => api.delete<void>(`/api/v1/admin/datasets/${datasetId}`),
}

export type {
  AdminCareerPath,
  AdminCourse,
  AdminDataset,
  AdminGlossaryTerm,
  AdminInterviewQuestion,
  AdminLesson,
  AdminModule,
  AdminProject,
  AdminProjectSubmission,
  AdminQuiz,
  AdminQuizQuestion,
  AdminResource,
  AdminTool,
}
