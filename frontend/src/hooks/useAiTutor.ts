import { useCallback, useRef, useState } from 'react'
import { aiTutorApi } from '@/services/aiTutorApi'
import type { ChatMessage, CreateSessionPayload } from '@/types/aiTutor'

const AI_TUTOR_WS_BASE = import.meta.env.VITE_API_WS_BASE_URL ?? 'ws://localhost:8000'

export function useAiTutor() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const socketRef = useRef<WebSocket | null>(null)

  const start = useCallback(async (payload: CreateSessionPayload) => {
    setError(null)
    setMessages([])
    const session = await aiTutorApi.createSession(payload)
    setSessionId(session.id)

    const socket = new WebSocket(`${AI_TUTOR_WS_BASE}/api/v1/ai-tutor/ws/${session.id}`)
    socketRef.current = socket
    return session
  }, [])

  const send = useCallback((text: string) => {
    const socket = socketRef.current
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('Not connected yet — try again in a moment.')
      return
    }

    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setStreaming(true)

    let assistantText = ''
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }])

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data) as { type: 'token' | 'done' | 'error'; data?: string }
      if (msg.type === 'token' && msg.data) {
        assistantText += msg.data
        setMessages((prev) => {
          const copy = [...prev]
          copy[copy.length - 1] = { role: 'assistant', content: assistantText }
          return copy
        })
      } else if (msg.type === 'error') {
        setError(msg.data ?? 'Something went wrong.')
        setMessages((prev) => prev.slice(0, -1))
        setStreaming(false)
      } else if (msg.type === 'done') {
        setStreaming(false)
      }
    }

    socket.send(JSON.stringify({ message: text }))
  }, [])

  return { messages, sessionId, streaming, error, start, send }
}
