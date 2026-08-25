/** Real statistics math backing the Stats Lab simulations — no charting
 * library needed since every plot here is either a parametric curve or a
 * histogram of numbers this module actually computes, not fetched or
 * faked. */

export function normalPdf(x: number, mean: number, stdDev: number): number {
  const variance = stdDev * stdDev
  return Math.exp(-((x - mean) ** 2) / (2 * variance)) / Math.sqrt(2 * Math.PI * variance)
}

/** Box-Muller transform — a standard, real method for generating normally
 * distributed random numbers from uniform ones. */
export function sampleNormal(mean: number, stdDev: number): number {
  const u1 = Math.random()
  const u2 = Math.random()
  const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2)
  return mean + z * stdDev
}

export function sampleUniform(min: number, max: number): number {
  return min + Math.random() * (max - min)
}

/** Exponential distribution via inverse transform sampling — a real
 * right-skewed population, used to demonstrate the CLT still applies to
 * non-normal populations. */
export function sampleExponential(rate: number): number {
  return -Math.log(1 - Math.random()) / rate
}

/** A genuine bimodal population: mixes two normals. */
export function sampleBimodal(): number {
  const pickFirst = Math.random() < 0.5
  return pickFirst ? sampleNormal(30, 8) : sampleNormal(70, 8)
}

export type PopulationShape = 'uniform' | 'skewed' | 'bimodal'

export function samplePopulation(shape: PopulationShape): number {
  switch (shape) {
    case 'uniform':
      return sampleUniform(0, 100)
    case 'skewed':
      return sampleExponential(0.05) // mean ~= 20, long right tail
    case 'bimodal':
      return sampleBimodal()
  }
}

export function mean(values: number[]): number {
  return values.reduce((a, b) => a + b, 0) / values.length
}

export function stdDev(values: number[]): number {
  const m = mean(values)
  const variance = values.reduce((sum, v) => sum + (v - m) ** 2, 0) / (values.length - 1)
  return Math.sqrt(variance)
}

/** Bins a set of values into `binCount` equal-width buckets between
 * [min, max], returning counts per bucket — the real computation behind
 * every histogram in the Stats Lab. */
export function histogramBins(values: number[], binCount: number, min: number, max: number): number[] {
  const bins = new Array(binCount).fill(0)
  const width = (max - min) / binCount
  for (const v of values) {
    if (v < min || v > max) continue
    const idx = Math.min(binCount - 1, Math.floor((v - min) / width))
    bins[idx]++
  }
  return bins
}

/** The z-score for a 95% two-tailed confidence interval — a fixed,
 * textbook constant (1.959964...), not something to recompute. */
export const Z_95 = 1.959963985
