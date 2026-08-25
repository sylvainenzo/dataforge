import { useMemo, useState } from 'react'
import { Card } from '@/components/ui/Card'
import { normalPdf } from '@/lib/statsMath'

const WIDTH = 640
const HEIGHT = 260
const PADDING = 32

export function NormalDistributionExplorer() {
  const [mean, setMean] = useState(0)
  const [sd, setSd] = useState(1)

  const { path, xMin, xMax } = useMemo(() => {
    const xMin = mean - 4 * sd - 1
    const xMax = mean + 4 * sd + 1
    const points = 200
    const values: { x: number; y: number }[] = []
    let maxY = 0
    for (let i = 0; i <= points; i++) {
      const x = xMin + ((xMax - xMin) * i) / points
      const y = normalPdf(x, mean, sd)
      maxY = Math.max(maxY, y)
      values.push({ x, y })
    }
    const toSvgX = (x: number) => PADDING + ((x - xMin) / (xMax - xMin)) * (WIDTH - 2 * PADDING)
    const toSvgY = (y: number) => HEIGHT - PADDING - (y / maxY) * (HEIGHT - 2 * PADDING)
    const path = values.map((p, i) => `${i === 0 ? 'M' : 'L'} ${toSvgX(p.x).toFixed(2)} ${toSvgY(p.y).toFixed(2)}`).join(' ')
    return { path, maxY, xMin, xMax }
  }, [mean, sd])

  const toSvgX = (x: number) => PADDING + ((x - xMin) / (xMax - xMin)) * (WIDTH - 2 * PADDING)

  const bands = [
    { sigma: 1, pct: '68%', opacity: 0.35 },
    { sigma: 2, pct: '95%', opacity: 0.2 },
    { sigma: 3, pct: '99.7%', opacity: 0.1 },
  ]

  return (
    <Card>
      <h2 className="mb-1 font-semibold text-text">Normal Distribution Explorer</h2>
      <p className="mb-4 text-sm text-text-muted">
        Drag the sliders — the curve is drawn live from the actual normal probability density function, not a
        pre-rendered image.
      </p>

      <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 flex items-center justify-between text-xs text-text-muted">
            <span>Mean (μ)</span>
            <span className="font-mono text-text">{mean.toFixed(1)}</span>
          </label>
          <input
            type="range"
            min={-10}
            max={10}
            step={0.1}
            value={mean}
            onChange={(e) => setMean(Number(e.target.value))}
            className="w-full accent-[var(--df-primary)]"
          />
        </div>
        <div>
          <label className="mb-1 flex items-center justify-between text-xs text-text-muted">
            <span>Standard deviation (σ)</span>
            <span className="font-mono text-text">{sd.toFixed(1)}</span>
          </label>
          <input
            type="range"
            min={0.5}
            max={5}
            step={0.1}
            value={sd}
            onChange={(e) => setSd(Number(e.target.value))}
            className="w-full accent-[var(--df-primary)]"
          />
        </div>
      </div>

      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full overflow-visible">
        <line x1={PADDING} y1={HEIGHT - PADDING} x2={WIDTH - PADDING} y2={HEIGHT - PADDING} stroke="var(--df-border)" />
        {bands
          .slice()
          .reverse()
          .map((band) => {
            const x1 = toSvgX(mean - band.sigma * sd)
            const x2 = toSvgX(mean + band.sigma * sd)
            return (
              <rect
                key={band.sigma}
                x={x1}
                y={PADDING}
                width={x2 - x1}
                height={HEIGHT - 2 * PADDING}
                fill="var(--df-primary)"
                opacity={band.opacity}
              />
            )
          })}
        <path d={path} fill="none" stroke="var(--df-primary)" strokeWidth={2.5} />
        <line
          x1={toSvgX(mean)}
          y1={PADDING}
          x2={toSvgX(mean)}
          y2={HEIGHT - PADDING}
          stroke="var(--df-text-muted)"
          strokeDasharray="4 3"
        />
      </svg>

      <div className="mt-2 flex justify-center gap-4 text-xs text-text-muted">
        {bands.map((b) => (
          <span key={b.sigma}>
            ±{b.sigma}σ ≈ {b.pct}
          </span>
        ))}
      </div>
    </Card>
  )
}
