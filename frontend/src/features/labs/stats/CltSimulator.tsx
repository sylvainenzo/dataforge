import { useMemo, useState } from 'react'
import { Card } from '@/components/ui/Card'
import { histogramBins, mean as computeMean, type PopulationShape, samplePopulation, stdDev } from '@/lib/statsMath'

const WIDTH = 640
const HEIGHT = 220
const PADDING = 32
const BIN_COUNT = 30
const DRAWS = 2000

const SHAPES: { value: PopulationShape; label: string }[] = [
  { value: 'uniform', label: 'Uniform' },
  { value: 'skewed', label: 'Skewed (exponential)' },
  { value: 'bimodal', label: 'Bimodal' },
]

function Histogram({ values, color }: { values: number[]; color: string }) {
  const { bars, min, max } = useMemo(() => {
    if (values.length === 0) return { bars: [], min: 0, max: 1 }
    const min = Math.min(...values)
    const max = Math.max(...values)
    const bins = histogramBins(values, BIN_COUNT, min, max)
    const maxCount = Math.max(...bins, 1)
    const barWidth = (WIDTH - 2 * PADDING) / BIN_COUNT
    const bars = bins.map((count, i) => {
      const height = (count / maxCount) * (HEIGHT - 2 * PADDING)
      return {
        x: PADDING + i * barWidth,
        y: HEIGHT - PADDING - height,
        width: Math.max(0, barWidth - 1),
        height,
      }
    })
    return { bars, min, max }
  }, [values])

  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full">
      <line x1={PADDING} y1={HEIGHT - PADDING} x2={WIDTH - PADDING} y2={HEIGHT - PADDING} stroke="var(--df-border)" />
      {bars.map((b, i) => (
        <rect key={i} x={b.x} y={b.y} width={b.width} height={b.height} fill={color} opacity={0.85} />
      ))}
      <text x={PADDING} y={HEIGHT - 8} className="fill-[var(--df-text-muted)] text-[10px]">
        {min.toFixed(1)}
      </text>
      <text x={WIDTH - PADDING} y={HEIGHT - 8} textAnchor="end" className="fill-[var(--df-text-muted)] text-[10px]">
        {max.toFixed(1)}
      </text>
    </svg>
  )
}

export function CltSimulator() {
  const [shape, setShape] = useState<PopulationShape>('skewed')
  const [sampleSize, setSampleSize] = useState(5)
  const [population, setPopulation] = useState<number[]>(() => Array.from({ length: DRAWS }, () => samplePopulation('skewed')))
  const [sampleMeans, setSampleMeans] = useState<number[]>([])
  const [drawing, setDrawing] = useState(false)

  function regeneratePopulation(newShape: PopulationShape) {
    setShape(newShape)
    setPopulation(Array.from({ length: DRAWS }, () => samplePopulation(newShape)))
    setSampleMeans([])
  }

  function drawSampleMeans() {
    setDrawing(true)
    const means: number[] = []
    for (let i = 0; i < DRAWS; i++) {
      const sample = Array.from({ length: sampleSize }, () => samplePopulation(shape))
      means.push(computeMean(sample))
    }
    setSampleMeans(means)
    setDrawing(false)
  }

  return (
    <Card>
      <h2 className="mb-1 font-semibold text-text">Central Limit Theorem Simulator</h2>
      <p className="mb-4 text-sm text-text-muted">
        The population below is genuinely not normal. Draw {DRAWS.toLocaleString()} real random samples of size{' '}
        <span className="font-mono text-text">n</span>, compute each sample's mean, and watch the distribution of
        those means approach normal as <span className="font-mono text-text">n</span> grows — this is the actual
        Central Limit Theorem, not an animation of it.
      </p>

      <div className="mb-4 flex flex-wrap items-end gap-4">
        <div>
          <label className="mb-1 block text-xs text-text-muted">Population shape</label>
          <div className="flex gap-1">
            {SHAPES.map((s) => (
              <button
                key={s.value}
                onClick={() => regeneratePopulation(s.value)}
                className={`rounded-md border px-2.5 py-1.5 text-xs font-medium transition-colors ${
                  shape === s.value
                    ? 'border-primary bg-primary-soft text-primary'
                    : 'border-border text-text-muted hover:bg-surface'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
        <div className="flex-1 min-w-[160px]">
          <label className="mb-1 flex items-center justify-between text-xs text-text-muted">
            <span>Sample size (n)</span>
            <span className="font-mono text-text">{sampleSize}</span>
          </label>
          <input
            type="range"
            min={1}
            max={50}
            value={sampleSize}
            onChange={(e) => setSampleSize(Number(e.target.value))}
            className="w-full accent-[var(--df-primary)]"
          />
        </div>
        <button
          onClick={drawSampleMeans}
          disabled={drawing}
          className="h-9 rounded-lg bg-primary px-4 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
        >
          Draw {DRAWS.toLocaleString()} samples
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <p className="mb-1 text-xs font-medium text-text-muted">
            Population (shape: {shape}, mean {computeMean(population).toFixed(1)}, sd {stdDev(population).toFixed(1)})
          </p>
          <Histogram values={population} color="var(--df-text-muted)" />
        </div>
        <div>
          <p className="mb-1 text-xs font-medium text-text-muted">
            {sampleMeans.length === 0
              ? `Distribution of sample means (n=${sampleSize}) — not drawn yet`
              : `Sample means (n=${sampleSize}, mean ${computeMean(sampleMeans).toFixed(1)}, sd ${stdDev(sampleMeans).toFixed(2)})`}
          </p>
          {sampleMeans.length === 0 ? (
            <div className="flex h-[220px] items-center justify-center rounded-lg border border-dashed border-border text-sm text-text-muted">
              Click "Draw samples" to see the sampling distribution
            </div>
          ) : (
            <Histogram values={sampleMeans} color="var(--df-primary)" />
          )}
        </div>
      </div>
    </Card>
  )
}
