import { cn } from '@/lib/cn'

interface ProgressBarProps {
  value: number // 0-100
  className?: string
  tone?: 'primary' | 'accent'
}

export function ProgressBar({ value, className, tone = 'primary' }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value))
  return (
    <div
      className={cn('h-1.5 w-full overflow-hidden rounded-full bg-surface', className)}
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className={cn('h-full rounded-full transition-[width]', tone === 'primary' ? 'bg-primary' : 'bg-accent')}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
