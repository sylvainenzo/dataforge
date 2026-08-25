import { Play, Square } from 'lucide-react'
import { useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { ExecutionOutputPanel } from '@/components/labs/ExecutionOutputPanel'
import { useExecution } from '@/hooks/useExecution'
import { CODE_LABS_ENABLED } from '@/lib/featureFlags'

const STARTER_CODE = `# Real matplotlib, real execution — save the figure and it renders
# in the Output panel, exactly like a chart in a notebook would.
import matplotlib.pyplot as plt

scores = [88, 72, 95, 61, 79, 85, 90, 68]

plt.figure(figsize=(6, 4))
plt.hist(scores, bins=6, edgecolor="white")
plt.title("Score Distribution")
plt.xlabel("Score")
plt.ylabel("Count")
plt.savefig("chart.png")
print("Saved chart.png")
`

export function DataVizLabPage() {
  const [code, setCode] = useState(STARTER_CODE)
  const { output, running, run, stop } = useExecution()

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-3">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text">Data Visualization Lab</h1>
          <p className="text-sm text-text-muted">
            Real matplotlib/seaborn charts, rendered from a real subprocess run — call{' '}
            <code className="rounded bg-surface px-1 py-0.5 font-mono text-xs">plt.savefig("chart.png")</code>{' '}
            and it appears in the Output panel. Not a pre-rendered image — the axes, colors, and title all come
            from your own code.
          </p>
        </div>
        {CODE_LABS_ENABLED ? (
          <Badge tone="warning">Dev sandbox</Badge>
        ) : (
          <Badge tone="error">Execution disabled</Badge>
        )}
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="flex flex-col overflow-hidden rounded-xl border border-border">
          <div className="flex items-center justify-between border-b border-border bg-surface px-3 py-2">
            <span className="font-mono text-xs text-text-muted">submission.py</span>
            <div className="flex gap-2">
              {running ? (
                <Button size="sm" variant="danger" onClick={stop}>
                  <Square className="h-3.5 w-3.5" /> Stop
                </Button>
              ) : (
                <Button size="sm" onClick={() => run(code)}>
                  <Play className="h-3.5 w-3.5" /> Run
                </Button>
              )}
            </div>
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck={false}
            className="h-96 flex-1 resize-none bg-card p-4 font-mono text-sm text-text focus:outline-none"
          />
        </div>

        <ExecutionOutputPanel output={output} running={running} />
      </div>
    </div>
  )
}
