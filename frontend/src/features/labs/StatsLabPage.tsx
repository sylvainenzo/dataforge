import { Badge } from '@/components/ui/Badge'
import { CltSimulator } from '@/features/labs/stats/CltSimulator'
import { ConfidenceIntervalSimulator } from '@/features/labs/stats/ConfidenceIntervalSimulator'
import { NormalDistributionExplorer } from '@/features/labs/stats/NormalDistributionExplorer'

export function StatsLabPage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text">Statistics Lab</h1>
          <p className="text-sm text-text-muted">
            Interactive simulations, not a code editor — every chart here is computed live from real random sampling
            and real probability math, not pre-rendered images.
          </p>
        </div>
        <Badge tone="primary">Interactive</Badge>
      </div>

      <NormalDistributionExplorer />
      <CltSimulator />
      <ConfidenceIntervalSimulator />
    </div>
  )
}
