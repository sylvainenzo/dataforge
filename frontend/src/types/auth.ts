export interface User {
  id: string
  email: string
  display_name: string | null
  is_active: boolean
  roles: string[]
}

export interface RegisterPayload {
  email: string
  password: string
  display_name: string
}

export interface LoginPayload {
  email: string
  password: string
}
