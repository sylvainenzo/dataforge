import { useCallback, useRef, useState } from 'react'
import { CODE_LABS_ENABLED } from '@/lib/featureFlags'

const EXECUTION_WS_URL = import.meta.env.VITE_EXECUTION_WS_URL ?? 'ws://localhost:8100/ws/execution'

export interface OutputLine {
  stream: 'stdout' | 'stderr' | 'exit' | 'system' | 'image'
  data: string
}

export function useExecution() {
  const [output, setOutput] = useState<OutputLine[]>([])
  const [running, setRunning] = useState(false)
  const socketRef = useRef<WebSocket | null>(null)

  const run = useCallback((code: string, language: string = 'python') => {
    setOutput([])

    if (!CODE_LABS_ENABLED) {
      setOutput([
        {
          stream: 'system',
          data: 'Code execution is temporarily disabled while the sandbox is hardened for public use. Try again later.',
        },
      ])
      return
    }

    setRunning(true)

    const socket = new WebSocket(EXECUTION_WS_URL)
    socketRef.current = socket

    socket.onopen = () => {
      socket.send(JSON.stringify({ code, language }))
    }

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data) as OutputLine
      setOutput((prev) => [...prev, msg])
      if (msg.stream === 'exit') {
        setRunning(false)
        socket.close()
      }
    }

    socket.onerror = () => {
      setOutput((prev) => [...prev, { stream: 'system', data: 'Connection error — is the execution service running?' }])
      setRunning(false)
    }

    socket.onclose = (event) => {
      setRunning(false)
      if (event.code === 4401) {
        setOutput((prev) => [...prev, { stream: 'system', data: 'Not authenticated — please sign in again.' }])
      } else if (event.code === 4429) {
        setOutput((prev) => [...prev, { stream: 'system', data: 'Rate limit exceeded — slow down and try again shortly.' }])
      }
    }
  }, [])

  const stop = useCallback(() => {
    socketRef.current?.close()
    setRunning(false)
  }, [])

  return { output, running, run, stop }
}
