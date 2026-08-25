import type { LucideIcon } from 'lucide-react'
import { EmptyState } from '@/components/ui/EmptyState'

interface ComingSoonPageProps {
  icon: LucideIcon
  title: string
  description: string
}

export function ComingSoonPage({ icon, title, description }: ComingSoonPageProps) {
  return (
    <div className="mx-auto max-w-2xl pt-12">
      <EmptyState icon={icon} title={title} description={description} />
    </div>
  )
}
