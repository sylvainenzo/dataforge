import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

type Tone = 'primary' | 'accent' | 'spark' | 'success' | 'warning' | 'error' | 'info' | 'neutral'

const toneStyles: Record<Tone, string> = {
  primary: 'bg-primary-soft text-primary',
  accent: 'bg-accent-soft text-accent',
  spark: 'bg-spark-soft text-spark',
  success: 'bg-success-soft text-success',
  warning: 'bg-warning-soft text-warning',
  error: 'bg-error-soft text-error',
  info: 'bg-info-soft text-info',
  neutral: 'bg-surface text-text-muted border border-border',
}

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone
}

export function Badge({ className, tone = 'neutral', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-md px-2 py-0.5 font-mono text-[11px] font-semibold uppercase tracking-wide',
        toneStyles[tone],
        className,
      )}
      {...props}
    />
  )
}
