import * as Dialog from '@radix-ui/react-dialog'
import { Send, Sparkles, X } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { Badge } from '@/components/ui/Badge'
import { useAiTutor } from '@/hooks/useAiTutor'
import { useUiStore } from '@/stores/uiStore'
import type { TutorMode } from '@/types/aiTutor'

const MODES: { value: TutorMode; label: string }[] = [
  { value: 'explain', label: 'Explain' },
  { value: 'hint', label: 'Hint' },
  { value: 'debug', label: 'Debug' },
  { value: 'quiz_me', label: 'Quiz me' },
]

export function AiTutorPanel() {
  const open = useUiStore((s) => s.aiTutorOpen)
  const setOpen = useUiStore((s) => s.setAiTutorOpen)
  const [mode, setMode] = useState<TutorMode>('explain')
  const [input, setInput] = useState('')
  const { messages, sessionId, streaming, error, start, send } = useAiTutor()

  async function handleStart(newMode: TutorMode) {
    setMode(newMode)
    await start({ mode: newMode })
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!input.trim()) return
    send(input)
    setInput('')
  }

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/40" />
        <Dialog.Content className="fixed right-0 top-0 z-50 flex h-screen w-full max-w-md flex-col border-l border-border bg-bg shadow-xl">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <Dialog.Title className="flex items-center gap-2 font-semibold text-text">
              <Sparkles className="h-4 w-4 text-primary" /> AI Tutor
            </Dialog.Title>
            <Dialog.Close className="text-text-muted hover:text-text">
              <X className="h-4 w-4" />
            </Dialog.Close>
          </div>

          {!sessionId ? (
            <div className="flex flex-1 flex-col items-center justify-center gap-3 p-6">
              <p className="text-center text-sm text-text-muted">What kind of help do you want?</p>
              <div className="grid grid-cols-2 gap-2">
                {MODES.map((m) => (
                  <button
                    key={m.value}
                    onClick={() => handleStart(m.value)}
                    className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text hover:border-primary hover:bg-primary-soft hover:text-primary"
                  >
                    {m.label}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              <div className="border-b border-border px-4 py-2">
                <Badge tone="primary">{MODES.find((m) => m.value === mode)?.label ?? mode}</Badge>
              </div>
              <div className="flex-1 space-y-3 overflow-y-auto p-4">
                {messages.map((m, i) => (
                  <div
                    key={i}
                    className={`rounded-lg px-3 py-2 text-sm ${
                      m.role === 'user' ? 'ml-8 bg-primary-soft text-primary' : 'mr-8 bg-card text-text'
                    }`}
                  >
                    {m.content || (streaming && i === messages.length - 1 ? '…' : '')}
                  </div>
                ))}
                {error && <p className="rounded-lg bg-error-soft px-3 py-2 text-sm text-error">{error}</p>}
              </div>
              <form onSubmit={onSubmit} className="flex gap-2 border-t border-border p-3">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask something…"
                  className="flex-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <button
                  type="submit"
                  disabled={streaming}
                  className="rounded-lg bg-primary px-3 py-2 text-white disabled:opacity-50"
                >
                  <Send className="h-4 w-4" />
                </button>
              </form>
            </>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
