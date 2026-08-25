import { api } from '@/lib/api'
import type { SqlExercise, SqlRunResult } from '@/types/sqlLab'

export const sqlLabApi = {
  exercises: () => api.get<SqlExercise[]>('/api/v1/sql-lab/exercises'),
  execute: (sql: string) => api.post<SqlRunResult>('/api/v1/sql-lab/execute', { sql }),
}
