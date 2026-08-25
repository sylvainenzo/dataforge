export interface DatasetSummary {
  id: string
  name: string
  slug: string
  description: string | null
  source: string
  license: string
  difficulty: string
  format: string
}

export interface ColumnProfile {
  name: string
  dtype: string
  missing_count: number
  missing_pct: number
  unique_count: number
}

export interface ProfilingResult {
  row_count: number
  column_count: number
  columns: ColumnProfile[]
  numeric_summary: Record<string, Record<string, number | null>>
  correlations: Record<string, Record<string, number | null>>
  outliers: Record<string, number>
}

export interface DatasetVersion {
  id: string
  version_number: number
  row_count: number | null
  column_count: number | null
  file_size_bytes: number | null
  profiling_status: string
  profiling_result: ProfilingResult | null
}

export interface DatasetDetail extends DatasetSummary {
  latest_version: DatasetVersion | null
}
