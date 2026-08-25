import { BarChart3, Calculator, Code2, Database, Sigma } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { CODE_LABS_ENABLED } from '@/lib/featureFlags'

const LABS = [
  { icon: Code2, name: 'Python Lab', to: '/labs/python', ready: true, needsSandbox: true },
  { icon: Database, name: 'SQL Lab', to: '/labs/sql', ready: true, needsSandbox: false },
  { icon: Calculator, name: 'R Lab', to: '/labs/r', ready: true, needsSandbox: true },
  { icon: Sigma, name: 'Statistics Lab', to: '/labs/statistics', ready: true, needsSandbox: false },
  { icon: BarChart3, name: 'Data Visualization Lab', to: '/labs/data-viz', ready: true, needsSandbox: true },
]

export function LabsIndexPage() {
  return (
    <div>
      <h1 className="mb-4 text-xl font-bold text-text">Labs</h1>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {LABS.map((lab) => {
          const available = lab.ready && (!lab.needsSandbox || CODE_LABS_ENABLED)
          return available ? (
            <Link key={lab.name} to={lab.to}>
              <Card className="flex h-full items-center gap-3 transition-colors hover:border-primary/50">
                <lab.icon className="h-6 w-6 text-primary" />
                <span className="font-semibold text-text">{lab.name}</span>
              </Card>
            </Link>
          ) : (
            <Card key={lab.name} className="flex items-center gap-3 opacity-60">
              <lab.icon className="h-6 w-6 text-text-muted" />
              <span className="font-semibold text-text">{lab.name}</span>
              <Badge tone="neutral" className="ml-auto">
                {lab.ready ? 'Sandbox hardening' : 'Coming later'}
              </Badge>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
