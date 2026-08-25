import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { datasetsApi } from '@/services/datasetsApi'

function cellTone(pct: number) {
  if (pct === 0) return 'text-text-muted'
  if (pct < 10) return 'text-warning'
  return 'text-error'
}

export function DatasetDetailPage() {
  const { slug = '' } = useParams()
  const { data: dataset, isLoading } = useQuery({ queryKey: ['datasets', slug], queryFn: () => datasetsApi.detail(slug) })

  if (isLoading) return <Skeleton className="h-96" />
  if (!dataset) return <p className="text-sm text-text-muted">Dataset not found.</p>

  const profile = dataset.latest_version?.profiling_result

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-1 flex items-center gap-2">
        <h1 className="text-xl font-bold text-text">{dataset.name}</h1>
        <Badge tone="primary">{dataset.format}</Badge>
      </div>
      <p className="mb-1 text-sm text-text-muted">{dataset.description}</p>
      <p className="mb-6 text-xs text-text-muted">
        Source: {dataset.source} · License: {dataset.license}
      </p>

      {!profile ? (
        <p className="text-sm text-text-muted">No profiling data available.</p>
      ) : (
        <div className="flex flex-col gap-5">
          <div className="flex gap-3">
            <Badge tone="accent">{profile.row_count} rows</Badge>
            <Badge tone="accent">{profile.column_count} columns</Badge>
          </div>

          <Card>
            <h2 className="mb-3 text-sm font-semibold text-text">Columns</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-border text-xs uppercase text-text-muted">
                    <th className="px-2 py-1.5">Column</th>
                    <th className="px-2 py-1.5">Type</th>
                    <th className="px-2 py-1.5">Missing</th>
                    <th className="px-2 py-1.5">Unique</th>
                    <th className="px-2 py-1.5">Outliers</th>
                  </tr>
                </thead>
                <tbody>
                  {profile.columns.map((col) => (
                    <tr key={col.name} className="border-b border-border last:border-0">
                      <td className="px-2 py-1.5 font-mono text-text">{col.name}</td>
                      <td className="px-2 py-1.5 font-mono text-text-muted">{col.dtype}</td>
                      <td className={`px-2 py-1.5 tabular-nums ${cellTone(col.missing_pct)}`}>
                        {col.missing_count} ({col.missing_pct}%)
                      </td>
                      <td className="px-2 py-1.5 tabular-nums text-text">{col.unique_count}</td>
                      <td className="px-2 py-1.5 tabular-nums text-text">{profile.outliers[col.name] ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {Object.keys(profile.numeric_summary).length > 0 && (
            <Card>
              <h2 className="mb-3 text-sm font-semibold text-text">Summary statistics</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-border text-xs uppercase text-text-muted">
                      <th className="px-2 py-1.5">Column</th>
                      <th className="px-2 py-1.5">Mean</th>
                      <th className="px-2 py-1.5">Std</th>
                      <th className="px-2 py-1.5">Min</th>
                      <th className="px-2 py-1.5">25%</th>
                      <th className="px-2 py-1.5">50%</th>
                      <th className="px-2 py-1.5">75%</th>
                      <th className="px-2 py-1.5">Max</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(profile.numeric_summary).map(([col, stats]) => (
                      <tr key={col} className="border-b border-border last:border-0">
                        <td className="px-2 py-1.5 font-mono text-text">{col}</td>
                        {['mean', 'std', 'min', '25%', '50%', '75%', 'max'].map((k) => (
                          <td key={k} className="px-2 py-1.5 tabular-nums text-text-muted">
                            {stats[k] ?? '—'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {Object.keys(profile.correlations).length > 0 && (
            <Card>
              <h2 className="mb-3 text-sm font-semibold text-text">Correlations</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-border text-xs uppercase text-text-muted">
                      <th className="px-2 py-1.5"></th>
                      {Object.keys(profile.correlations).map((col) => (
                        <th key={col} className="px-2 py-1.5 font-mono">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(profile.correlations).map(([col, row]) => (
                      <tr key={col} className="border-b border-border last:border-0">
                        <td className="px-2 py-1.5 font-mono text-text">{col}</td>
                        {Object.entries(row).map(([other, val]) => (
                          <td
                            key={other}
                            className="px-2 py-1.5 tabular-nums text-text-muted"
                            style={{ opacity: val === null ? 0.4 : 0.5 + Math.abs(val) * 0.5 }}
                          >
                            {val ?? '—'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
