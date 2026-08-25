import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ApiError } from '@/lib/api'
import { authApi } from '@/services/authApi'
import type { LoginPayload, RegisterPayload } from '@/types/auth'

export const AUTH_QUERY_KEY = ['auth', 'me']

/** The current session, sourced from the httpOnly cookie set by the API —
 * there is no client-side token to manage. A 401 just means "signed out,"
 * not an error worth surfacing, so it's treated as `user: null` rather than
 * an error state. */
export function useCurrentUser() {
  const query = useQuery({
    queryKey: AUTH_QUERY_KEY,
    queryFn: async () => {
      try {
        return await authApi.me()
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return null
        throw err
      }
    },
    retry: false,
    staleTime: 60_000,
  })

  return { user: query.data ?? null, isLoading: query.isLoading }
}

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: LoginPayload) => authApi.login(payload),
    onSuccess: (user) => queryClient.setQueryData(AUTH_QUERY_KEY, user),
  })
}

export function useRegister() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: RegisterPayload) => authApi.register(payload),
    onSuccess: (user) => queryClient.setQueryData(AUTH_QUERY_KEY, user),
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => queryClient.setQueryData(AUTH_QUERY_KEY, null),
  })
}
