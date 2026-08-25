/** Opt-out flag: unset (local/dev) or anything other than "false" keeps the
 * free-form code-execution labs (Python/R/Data Viz) on. Set
 * VITE_CODE_LABS_ENABLED=false at build time to gate them off — for a
 * public launch before the execution-service runs behind a real sandbox
 * (gVisor/Firecracker), not this dev build's resource-limited subprocess.
 * SQL Lab (validated, read-only-role queries) and Statistics Lab (no code
 * execution at all) are unaffected — neither needs the sandbox. */
export const CODE_LABS_ENABLED = import.meta.env.VITE_CODE_LABS_ENABLED !== 'false'
