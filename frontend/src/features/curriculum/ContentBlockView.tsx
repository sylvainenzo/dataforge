import { AlertTriangle, Target } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import type { ContentBlock } from '@/types/curriculum'

export function ContentBlockView({ block }: { block: ContentBlock }) {
  switch (block.type) {
    case 'objectives':
      return (
        <Card>
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-text">
            <Target className="h-4 w-4 text-primary" />
            What you will learn
          </div>
          <ul className="list-inside list-disc space-y-1 text-sm text-text-muted">
            {block.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>
      )

    case 'explanation':
      return (
        <div className="space-y-3">
          <p className="text-sm leading-relaxed text-text">{block.beginner}</p>
          <details className="rounded-lg border border-border bg-surface p-3">
            <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-text-muted">
              Technical detail
            </summary>
            <p className="mt-2 text-sm leading-relaxed text-text-muted">{block.technical}</p>
          </details>
        </div>
      )

    case 'code':
      return (
        <div className="overflow-hidden rounded-lg border border-border">
          <div className="border-b border-border bg-surface px-3 py-1.5 font-mono text-xs text-text-muted">
            {block.language}
          </div>
          <pre className="overflow-x-auto bg-card p-4 font-mono text-sm text-text">
            <code>{block.code}</code>
          </pre>
          {block.output && (
            <pre className="overflow-x-auto whitespace-pre border-t border-border bg-bg px-4 py-3 font-mono text-xs text-text-muted">
              <span className="text-accent"># Output</span>
              {'\n'}
              {block.output}
            </pre>
          )}
        </div>
      )

    case 'exercise':
      return (
        <Card className="border-primary/30">
          <div className="mb-2 text-sm font-semibold text-text">Try it yourself</div>
          <p className="mb-3 text-sm text-text-muted">{block.prompt}</p>
          <pre className="overflow-x-auto rounded-lg bg-surface p-3 font-mono text-sm text-text">
            <code>{block.starter_code}</code>
          </pre>
          <p className="mt-2 text-xs text-text-muted">
            Try this in the matching Lab (see Labs in the sidebar) for an interactive editor.
          </p>
        </Card>
      )

    case 'common_mistakes':
      return (
        <Card>
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-text">
            <AlertTriangle className="h-4 w-4 text-warning" />
            Common mistakes
          </div>
          <ul className="list-inside list-disc space-y-1 text-sm text-text-muted">
            {block.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>
      )

    case 'summary':
      return (
        <div className="rounded-lg bg-primary-soft p-4 text-sm text-primary">
          <span className="font-semibold">Summary: </span>
          {block.text}
        </div>
      )

    case 'key_terms':
      return (
        <div className="flex flex-wrap gap-2">
          {block.items.map((term) => (
            <span key={term} className="rounded-md border border-border bg-surface px-2 py-1 font-mono text-xs text-text-muted">
              {term}
            </span>
          ))}
        </div>
      )

    default:
      return null
  }
}
