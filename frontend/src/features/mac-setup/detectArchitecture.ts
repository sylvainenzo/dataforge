import type { Architecture } from '@/types/tools'

/** Best-effort only — Phase 1 §11 is explicit that client-reported
 * architecture is a hint, never trusted for anything security-relevant,
 * and must always be paired with an explicit user-editable toggle.
 * navigator.userAgent alone is unreliable for this (Safari/Chrome report
 * "Intel Mac OS X" in the UA string even on Apple Silicon for legacy
 * compatibility reasons), so this uses the Chromium-only User-Agent Client
 * Hints API when available and otherwise honestly returns null rather than
 * guessing. */
export async function detectArchitecture(): Promise<Architecture | null> {
  const uaData = (navigator as unknown as { userAgentData?: { getHighEntropyValues: (hints: string[]) => Promise<{ architecture?: string }> } }).userAgentData
  if (!uaData) return null

  try {
    const { architecture } = await uaData.getHighEntropyValues(['architecture'])
    if (architecture === 'arm') return 'apple_silicon'
    if (architecture === 'x86') return 'intel'
  } catch {
    // Client Hints can throw if the permission policy blocks it — treat as undetected.
  }
  return null
}
