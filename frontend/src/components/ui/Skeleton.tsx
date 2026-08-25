import { cn } from '@/lib/cn'

/** Required loading state per Phase 1 §30: skeletons for content, never a
 * spinner (spinners are reserved for discrete actions like a button
 * submit). */
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-md bg-surface', className)} />
}
