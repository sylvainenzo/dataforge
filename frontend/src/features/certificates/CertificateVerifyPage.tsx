import { useMutation } from '@tanstack/react-query'
import { CheckCircle2, ShieldCheck, XCircle } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { ApiError } from '@/lib/api'
import { certificatesApi } from '@/services/certificatesApi'
import type { CertificateVerification } from '@/types/certificates'

export function CertificateVerifyPage() {
  const { certificateNumber: paramNumber } = useParams()
  const [number, setNumber] = useState(paramNumber ?? '')
  const [result, setResult] = useState<CertificateVerification | null>(null)
  const [notFound, setNotFound] = useState(false)

  const verifyMutation = useMutation({
    mutationFn: (n: string) => certificatesApi.verify(n),
    onSuccess: (data) => {
      setResult(data)
      setNotFound(false)
    },
    onError: (err) => {
      setResult(null)
      setNotFound(err instanceof ApiError && err.status === 404)
    },
  })

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    setResult(null)
    setNotFound(false)
    verifyMutation.mutate(number)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 flex flex-col items-center gap-2">
          <ShieldCheck className="h-8 w-8 text-primary" />
          <h1 className="text-lg font-bold text-text">Verify a DataForge Certificate</h1>
        </div>

        <form onSubmit={onSubmit} className="flex gap-2 rounded-xl border border-border bg-card p-4">
          <div className="flex-1">
            <Input
              placeholder="DF-XXXXXXXX"
              required
              value={number}
              onChange={(e) => setNumber(e.target.value.toUpperCase())}
            />
          </div>
          <Button type="submit" disabled={verifyMutation.isPending}>
            Verify
          </Button>
        </form>

        {result && (
          <div className="mt-4 flex items-start gap-3 rounded-xl border border-success/30 bg-success-soft p-4">
            <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-success" />
            <div className="text-sm">
              <p className="font-semibold text-text">Valid certificate</p>
              <p className="mt-1 text-text-muted">
                <span className="font-medium text-text">{result.recipient_name}</span> completed{' '}
                <span className="font-medium text-text">{result.course_title}</span> on{' '}
                {new Date(result.issued_at).toLocaleDateString()}.
              </p>
            </div>
          </div>
        )}

        {notFound && (
          <div className="mt-4 flex items-center gap-3 rounded-xl border border-error/30 bg-error-soft p-4">
            <XCircle className="h-5 w-5 shrink-0 text-error" />
            <p className="text-sm text-text">No certificate found with that number.</p>
          </div>
        )}
      </div>
    </div>
  )
}
