import type { OutputLine } from '@/hooks/useExecution'

export function ExecutionOutputPanel({ output, running }: { output: OutputLine[]; running: boolean }) {
  return (
    <div className="flex flex-col overflow-hidden rounded-xl border border-border">
      <div className="border-b border-border bg-surface px-3 py-2 font-mono text-xs text-text-muted">Output</div>
      <div className="h-96 flex-1 overflow-y-auto bg-bg p-4 font-mono text-sm">
        {output.length === 0 && !running && <p className="text-text-muted">Run your code to see output here.</p>}
        {output.map((line, i) => {
          if (line.stream === 'image') {
            return (
              <img
                key={i}
                src={`data:image/png;base64,${line.data}`}
                alt="Generated chart"
                className="my-2 max-w-full rounded-lg border border-border"
              />
            )
          }
          return (
            <div
              key={i}
              className={
                line.stream === 'stderr'
                  ? 'text-error'
                  : line.stream === 'system'
                    ? 'text-warning'
                    : line.stream === 'exit'
                      ? 'text-text-muted'
                      : 'text-text'
              }
            >
              {line.stream === 'exit' ? `[process exited with code ${line.data}]` : line.data}
            </div>
          )
        })}
        {running && <div className="animate-pulse text-accent">●</div>}
      </div>
    </div>
  )
}
