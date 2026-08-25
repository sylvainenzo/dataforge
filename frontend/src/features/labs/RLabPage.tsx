import { Play, Square } from 'lucide-react'
import { useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { ExecutionOutputPanel } from '@/components/labs/ExecutionOutputPanel'
import { useExecution } from '@/hooks/useExecution'
import { CODE_LABS_ENABLED } from '@/lib/featureFlags'

const STARTER_CODE = `# Try it — this runs for real, in an isolated R process on the server.
scores <- c(88, 72, 95, 61, 79)

cat("mean:  ", mean(scores), "\\n")
cat("median:", median(scores), "\\n")
cat("sd:    ", sd(scores), "\\n")

passing <- scores[scores >= 70]
print(passing)
`

export function RLabPage() {
  const [code, setCode] = useState(STARTER_CODE)
  const { output, running, run, stop } = useExecution()

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-3">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text">R Lab</h1>
          <p className="text-sm text-text-muted">
            Real R code, real execution, per the Phase 1 §7 sandbox design — but this dev build runs in a
            local, resource-limited subprocess, not the gVisor container the production architecture calls for.
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
            <span className="font-mono text-xs text-text-muted">submission.R</span>
            <div className="flex gap-2">
              {running ? (
                <Button size="sm" variant="danger" onClick={stop}>
                  <Square className="h-3.5 w-3.5" /> Stop
                </Button>
              ) : (
                <Button size="sm" onClick={() => run(code, 'r')}>
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
