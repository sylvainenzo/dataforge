import { api } from '@/lib/api'
import type { LoginPayload, RegisterPayload, User } from '@/types/auth'

export const authApi = {
  me: () => api.get<User>('/api/v1/auth/me'),
  register: (payload: RegisterPayload) => api.post<User>('/api/v1/auth/register', payload),
  login: (payload: LoginPayload) => api.post<User>('/api/v1/auth/login', payload),
  logout: () => api.post<{ message: string }>('/api/v1/auth/logout'),
  updateProfile: (display_name: string) => api.patch<User>('/api/v1/auth/me', { display_name }),
  changePassword: (current_password: string, new_password: string) =>
    api.post<{ message: string }>('/api/v1/auth/change-password', { current_password, new_password }),
  forgotPassword: (email: string) => api.post<{ message: string }>('/api/v1/auth/forgot-password', { email }),
  resetPassword: (token: string, new_password: string) =>
    api.post<{ message: string }>('/api/v1/auth/reset-password', { token, new_password }),
}
