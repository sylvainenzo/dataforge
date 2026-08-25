import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { curriculumApi } from '@/services/curriculumApi'

export function useLearningPaths() {
  return useQuery({ queryKey: ['learning-paths'], queryFn: curriculumApi.learningPaths })
}

export function useLearningPath(slug: string) {
  return useQuery({ queryKey: ['learning-paths', slug], queryFn: () => curriculumApi.learningPath(slug) })
}

export function useCourses() {
  return useQuery({ queryKey: ['courses'], queryFn: curriculumApi.courses })
}

export function useCourse(slug: string) {
  return useQuery({ queryKey: ['courses', slug], queryFn: () => curriculumApi.course(slug) })
}

export function useLesson(slug: string) {
  return useQuery({ queryKey: ['lessons', slug], queryFn: () => curriculumApi.lesson(slug) })
}

export function useCompleteLesson(slug: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => curriculumApi.completeLesson(slug),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lessons', slug] }),
  })
}

export function useQuiz(id: string) {
  return useQuery({ queryKey: ['quizzes', id], queryFn: () => curriculumApi.quiz(id), enabled: !!id })
}

export function useSubmitQuiz(id: string) {
  return useMutation({
    mutationFn: (answers: Record<string, string>) => curriculumApi.submitQuiz(id, answers),
  })
}
