import { useMutation } from '@tanstack/react-query'
import { Cpu, Terminal } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { detectArchitecture } from '@/features/mac-setup/detectArchitecture'
import { toolsApi } from '@/services/toolsApi'
import type { Architecture, Experience } from '@/types/tools'

const CAREERS = [
  { value: 'data-analyst', label: 'Data Analyst' },
  { value: 'data-scientist', label: 'Data Scientist' },
  { value: 'data-engineer', label: 'Data Engineer' },
  { value: 'ml-engineer', label: 'ML Engineer' },
  { value: 'analytics-engineer', label: 'Analytics Engineer' },
  { value: 'bi-analyst', label: 'BI Analyst' },
]

export function MacSetupPage() {
  const [step, setStep] = useState(1)
  const [architecture, setArchitecture] = useState<Architecture>('apple_silicon')
  const [architectureDetected, setArchitectureDetected] = useState(false)
  const [career, setCareer] = useState('data-analyst')
  const [experience, setExperience] = useState<Experience>('beginner')

  const checklist = useMutation({
    mutationFn: () => toolsApi.checklist(architecture, career, experience),
  })

  useEffect(() => {
    detectArchitecture().then((detected) => {
      if (detected) {
        setArchitecture(detected)
        setArchitectureDetected(true)
      }
    })
  }, [])

  if (step === 4 && checklist.data) {
    return (
      <div className="mx-auto max-w-2xl">
        <h1 className="mb-1 text-xl font-bold text-text">Your setup checklist</h1>
        <p className="mb-6 text-sm text-text-muted">
          {CAREERS.find((c) => c.value === career)?.label} · {experience} · {architecture === 'apple_silicon' ? 'Apple Silicon' : 'Intel'}
        </p>

        <div className="space-y-3">
          {checklist.data.map(({ tool, essential, reason }) => (
            <Card key={tool.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="mb-1 flex items-center gap-2">
                    <h3 className="font-semibold text-text">{tool.name}</h3>
                    <Badge tone={essential ? 'primary' : 'neutral'}>{essential ? 'Essential' : 'Optional'}</Badge>
                  </div>
                  <p className="text-sm text-text-muted">{reason}</p>
                </div>
                <Link
                  to={`/tools/${tool.slug}`}
                  className="flex shrink-0 items-center gap-1 text-xs font-medium text-primary hover:underline"
                >
                  <Terminal className="h-3.5 w-3.5" /> Install guide
                </Link>
              </div>
            </Card>
          ))}
        </div>

        <Button variant="secondary" className="mt-6" onClick={() => setStep(1)}>
          Start over
        </Button>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-1 text-xl font-bold text-text">Mac Setup Wizard</h1>
      <p className="mb-6 text-sm text-text-muted">Step {step} of 3</p>

      {step === 1 && (
        <Card>
          <div className="mb-4 flex items-center gap-2">
            <Cpu className="h-5 w-5 text-primary" />
            <h2 className="font-semibold text-text">What Mac do you have?</h2>
          </div>
          {architectureDetected && (
            <p className="mb-3 text-xs text-accent">Detected automatically — change it below if this is wrong.</p>
          )}
          <div className="mb-6 grid grid-cols-2 gap-3">
            {(['apple_silicon', 'intel'] as const).map((arch) => (
              <button
                key={arch}
                onClick={() => setArchitecture(arch)}
                className={`rounded-lg border p-4 text-sm font-medium transition-colors ${
                  architecture === arch ? 'border-primary bg-primary-soft text-primary' : 'border-border text-text hover:bg-surface'
                }`}
              >
                {arch === 'apple_silicon' ? 'Apple Silicon (M1/M2/M3/M4)' : 'Intel'}
              </button>
            ))}
          </div>
          <Button onClick={() => setStep(2)}>Continue</Button>
        </Card>
      )}

      {step === 2 && (
        <Card>
          <h2 className="mb-4 font-semibold text-text">What are you working toward?</h2>
          <div className="mb-6 grid grid-cols-2 gap-2">
            {CAREERS.map((c) => (
              <button
                key={c.value}
                onClick={() => setCareer(c.value)}
                className={`rounded-lg border p-3 text-left text-sm font-medium transition-colors ${
                  career === c.value ? 'border-primary bg-primary-soft text-primary' : 'border-border text-text hover:bg-surface'
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setStep(1)}>
              Back
            </Button>
            <Button onClick={() => setStep(3)}>Continue</Button>
          </div>
        </Card>
      )}

      {step === 3 && (
        <Card>
          <h2 className="mb-4 font-semibold text-text">How much programming experience do you have?</h2>
          <div className="mb-6 space-y-2">
            {(['beginner', 'intermediate', 'advanced'] as const).map((exp) => (
              <button
                key={exp}
                onClick={() => setExperience(exp)}
                className={`block w-full rounded-lg border p-3 text-left text-sm font-medium capitalize transition-colors ${
                  experience === exp ? 'border-primary bg-primary-soft text-primary' : 'border-border text-text hover:bg-surface'
                }`}
              >
                {exp}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setStep(2)}>
              Back
            </Button>
            <Button
              onClick={() => {
                checklist.mutate(undefined, { onSuccess: () => setStep(4) })
              }}
              disabled={checklist.isPending}
            >
              {checklist.isPending ? 'Building your checklist…' : 'Generate checklist'}
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}
