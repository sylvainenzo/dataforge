import { useQuery } from '@tanstack/react-query'
import { Lightbulb, Play } from 'lucide-react'
import { useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { ApiError } from '@/lib/api'
import { sqlLabApi } from '@/services/sqlLabApi'
import type { SqlRunResult } from '@/types/sqlLab'

export function SqlLabPage() {
  const { data: exercises, isLoading } = useQuery({ queryKey: ['sql-lab', 'exercises'], queryFn: sqlLabApi.exercises })
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [showHint, setShowHint] = useState(false)
  const [sql, setSql] = useState('SELECT * FROM employees LIMIT 10;')
  const [result, setResult] = useState<SqlRunResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [running, setRunning] = useState(false)

  const selected = exercises?.find((e) => e.id === selectedId)

  async function runQuery() {
    setRunning(true)
    setError(null)
    setResult(null)
    try {
      const res = await sqlLabApi.execute(sql)
      setResult(res)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong.')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="mx-auto grid max-w-6xl grid-cols-1 gap-4 md:grid-cols-[280px_1fr]">
      <div>
        <h1 className="mb-1 text-xl font-bold text-text">SQL Lab</h1>
        <p className="mb-4 text-sm text-text-muted">
          Real Postgres, read-only. Schema: <code className="font-mono text-xs">employees</code>,{' '}
          <code className="font-mono text-xs">departments</code>.
        </p>

        {isLoading ? (
          <Skeleton className="h-48" />
        ) : (
          <div className="space-y-2">
            {exercises?.map((ex) => (
              <button
                key={ex.id}
                onClick={() => {
                  setSelectedId(ex.id)
                  setShowHint(false)
                }}
                className={`block w-full rounded-lg border p-3 text-left text-sm transition-colors ${
                  selectedId === ex.id ? 'border-primary bg-primary-soft text-primary' : 'border-border text-text hover:bg-surface'
                }`}
              >
                {ex.title}
              </button>
            ))}
          </div>
        )}

        {selected && (
          <Card className="mt-4">
            <p className="mb-2 text-sm text-text">{selected.prompt}</p>
            {showHint ? (
              <p className="rounded-lg bg-warning-soft p-2 font-mono text-xs text-warning">{selected.hint}</p>
            ) : (
              <Button size="sm" variant="secondary" onClick={() => setShowHint(true)}>
                <Lightbulb className="h-3.5 w-3.5" /> Show hint
              </Button>
            )}
          </Card>
        )}
      </div>

      <div className="flex flex-col gap-3">
        <div className="overflow-hidden rounded-xl border border-border">
          <div className="flex items-center justify-between border-b border-border bg-surface px-3 py-2">
            <span className="font-mono text-xs text-text-muted">query.sql</span>
            <Button size="sm" onClick={runQuery} disabled={running}>
              <Play className="h-3.5 w-3.5" /> {running ? 'Running…' : 'Run'}
            </Button>
          </div>
          <textarea
            value={sql}
            onChange={(e) => setSql(e.target.value)}
            spellCheck={false}
            className="h-40 w-full resize-none bg-card p-4 font-mono text-sm text-text focus:outline-none"
          />
        </div>

        <div className="overflow-hidden rounded-xl border border-border">
          <div className="border-b border-border bg-surface px-3 py-2 font-mono text-xs text-text-muted">Results</div>
          <div className="max-h-96 overflow-auto p-4">
            {error && <p className="font-mono text-sm text-error">{error}</p>}
            {!error && !result && <p className="text-sm text-text-muted">Run a query to see results.</p>}
            {result && (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-border">
                        {result.columns.map((col) => (
                          <th key={col} className="px-3 py-2 font-mono text-xs font-semibold uppercase text-text-muted">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.rows.map((row, i) => (
                        <tr key={i} className="border-b border-border last:border-0">
                          {row.map((cell, j) => (
                            <td key={j} className="px-3 py-2 font-mono text-text tabular-nums">
                              {String(cell)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <Badge tone="accent">{result.row_count} rows</Badge>
                  {result.truncated && <Badge tone="warning">Truncated at 500 rows</Badge>}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
