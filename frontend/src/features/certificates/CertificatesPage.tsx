import { useQuery } from '@tanstack/react-query'
import { Award, Download } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { certificatesApi } from '@/services/certificatesApi'

export function CertificatesPage() {
  const { data: certificates, isLoading } = useQuery({ queryKey: ['certificates'], queryFn: certificatesApi.list })

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-1 text-xl font-bold text-text">Certificates</h1>
      <p className="mb-4 text-sm text-text-muted">
        Earned by completing every lesson in a course. Anyone can verify a certificate number at{' '}
        <code className="rounded bg-surface px-1 py-0.5 font-mono text-xs">/certificates/verify</code>.
      </p>

      {isLoading ? (
        <Skeleton className="h-32" />
      ) : !certificates || certificates.length === 0 ? (
        <EmptyState
          icon={Award}
          title="No certificates yet"
          description="Complete every lesson in a course, then request a certificate from that course's page."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {certificates.map((cert) => (
            <Card key={cert.id} className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent-soft">
                <Award className="h-5 w-5 text-accent" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-text">{cert.title}</p>
                <p className="font-mono text-xs text-text-muted">
                  {cert.certificate_number} · issued {new Date(cert.issued_at).toLocaleDateString()}
                </p>
              </div>
              <a
                href={certificatesApi.downloadUrl(cert.id)}
                className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-sm text-text-muted hover:border-primary hover:text-primary"
              >
                <Download className="h-3.5 w-3.5" /> PDF
              </a>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
