export interface SqlExercise {
  id: string
  title: string
  prompt: string
  hint: string
  schema_description: string
}

export interface SqlRunResult {
  columns: string[]
  rows: unknown[][]
  truncated: boolean
  row_count: number
}
