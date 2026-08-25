import { useState } from 'react'
import { Card } from '@/components/ui/Card'
import { mean as computeMean, sampleNormal, stdDev, Z_95 } from '@/lib/statsMath'

const TRUE_MEAN = 100
const TRUE_SD = 15
const WIDTH = 640
const ROW_HEIGHT = 18
const PADDING = 40

interface IntervalResult {
  low: number
  high: number
  sampleMean: number
  contains: boolean
}

export function ConfidenceIntervalSimulator() {
  const [sampleSize, setSampleSize] = useState(30)
  const [intervals, setIntervals] = useState<IntervalResult[]>([])

  function draw20() {
    const results: IntervalResult[] = []
    for (let i = 0; i < 20; i++) {
      const sample = Array.from({ length: sampleSize }, () => sampleNormal(TRUE_MEAN, TRUE_SD))
      const sampleMean = computeMean(sample)
      const sampleSd = sampleSize > 1 ? stdDev(sample) : TRUE_SD
      const marginOfError = Z_95 * (sampleSd / Math.sqrt(sampleSize))
      const low = sampleMean - marginOfError
      const high = sampleMean + marginOfError
      results.push({ low, high, sampleMean, contains: TRUE_MEAN >= low && TRUE_MEAN <= high })
    }
    setIntervals(results)
  }

  const containedCount = intervals.filter((r) => r.contains).length

  const xMin = TRUE_MEAN - 3.2 * (TRUE_SD / Math.sqrt(Math.max(sampleSize, 4)))
  const xMax = TRUE_MEAN + 3.2 * (TRUE_SD / Math.sqrt(Math.max(sampleSize, 4)))
  const toSvgX = (x: number) => PADDING + ((x - xMin) / (xMax - xMin)) * (WIDTH - 2 * PADDING)
  const height = Math.max(intervals.length * ROW_HEIGHT + 20, 40)

  return (
    <Card>
      <h2 className="mb-1 font-semibold text-text">Confidence Interval Simulator</h2>
      <p className="mb-4 text-sm text-text-muted">
        The true population mean is fixed at <span className="font-mono text-text">μ = {TRUE_MEAN}</span> (you get
        to know it here — a real analyst never would). Each row draws a genuine random sample and builds a real 95%
        confidence interval from it. A 95% CI doesn't mean "95% chance this interval contains the mean" — it means
        that if you repeated this process many times, about 95% of the intervals would contain the true mean. Draw a
        batch and see for yourself.
      </p>

      <div className="mb-4 flex flex-wrap items-end gap-4">
        <div className="flex-1 min-w-[160px]">
          <label className="mb-1 flex items-center justify-between text-xs text-text-muted">
            <span>Sample size (n)</span>
            <span className="font-mono text-text">{sampleSize}</span>
          </label>
          <input
            type="range"
            min={5}
            max={100}
            value={sampleSize}
            onChange={(e) => setSampleSize(Number(e.target.value))}
            className="w-full accent-[var(--df-primary)]"
          />
        </div>
        <button
          onClick={draw20}
          className="h-9 rounded-lg bg-primary px-4 text-sm font-medium text-white hover:opacity-90"
        >
          Draw 20 samples &amp; intervals
        </button>
        {intervals.length > 0 && (
          <span className="text-sm text-text-muted">
            <span className={containedCount >= 17 ? 'font-semibold text-success' : 'font-semibold text-warning'}>
              {containedCount}/20
            </span>{' '}
            intervals contain μ
          </span>
        )}
      </div>

      {intervals.length === 0 ? (
        <div className="flex h-20 items-center justify-center rounded-lg border border-dashed border-border text-sm text-text-muted">
          Click "Draw 20 samples" to see confidence intervals
        </div>
      ) : (
        <svg viewBox={`0 0 ${WIDTH} ${height}`} className="w-full">
          <line
            x1={toSvgX(TRUE_MEAN)}
            y1={0}
            x2={toSvgX(TRUE_MEAN)}
            y2={height - 16}
            stroke="var(--df-text)"
            strokeDasharray="3 3"
          />
          {intervals.map((r, i) => {
            const y = 8 + i * ROW_HEIGHT
            return (
              <g key={i}>
                <line
                  x1={toSvgX(r.low)}
                  y1={y}
                  x2={toSvgX(r.high)}
                  y2={y}
                  stroke={r.contains ? 'var(--df-success)' : 'var(--df-error)'}
                  strokeWidth={3}
                />
                <circle cx={toSvgX(r.sampleMean)} cy={y} r={2.5} fill="var(--df-text)" />
              </g>
            )
          })}
          <text x={toSvgX(TRUE_MEAN)} y={height - 4} textAnchor="middle" className="fill-[var(--df-text-muted)] text-[10px]">
            true μ = {TRUE_MEAN}
          </text>
        </svg>
      )}
    </Card>
  )
}
