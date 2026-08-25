import { describe, expect, it } from 'vitest'
import { cn } from './cn'

describe('cn', () => {
  it('merges plain class strings', () => {
    expect(cn('a', 'b')).toBe('a b')
  })

  it('drops falsy values', () => {
    expect(cn('a', false && 'b', undefined, null, 'c')).toBe('a c')
  })

  it('lets a later conflicting Tailwind class win', () => {
    // tailwind-merge's whole job: last utility in the same group wins
    expect(cn('px-2', 'px-4')).toBe('px-4')
  })

  it('keeps non-conflicting classes from both sides', () => {
    // text-sm (size) and text-error (color) are different utility groups —
    // tailwind-merge only drops same-group conflicts, so both survive.
    expect(cn('text-sm font-medium', 'text-error')).toBe('text-sm font-medium text-error')
  })

  it('lets a later conflicting text-color class win over an earlier one', () => {
    expect(cn('text-sm text-muted', 'text-error')).toBe('text-sm text-error')
  })
})
