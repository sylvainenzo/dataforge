import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Database, Upload } from 'lucide-react'
import { type FormEvent, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input } from '@/components/ui/Input'
import { Skeleton } from '@/components/ui/Skeleton'
import { ApiError } from '@/lib/api'
import { datasetsApi } from '@/services/datasetsApi'

export function DatasetsPage() {
  const queryClient = useQueryClient()
  const { data: datasets, isLoading } = useQuery({ queryKey: ['datasets'], queryFn: datasetsApi.list })
  const [showUpload, setShowUpload] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const file = fileInputRef.current?.files?.[0]
    if (!file) {
      setError('Choose a file first.')
      return
    }
    setUploading(true)
    setError(null)
    try {
      await datasetsApi.upload(file, name, description)
      await queryClient.invalidateQueries({ queryKey: ['datasets'] })
      setShowUpload(false)
      setName('')
      setDescription('')
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-text">Datasets</h1>
        <Button size="sm" onClick={() => setShowUpload((v) => !v)}>
          <Upload className="h-3.5 w-3.5" /> Upload
        </Button>
      </div>

      {showUpload && (
        <Card className="mb-6">
          <form onSubmit={onSubmit} className="flex flex-col gap-3">
            <Input label="Name" required value={name} onChange={(e) => setName(e.target.value)} />
            <Input label="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
            <div>
              <label className="mb-1.5 block text-sm font-medium text-text">File (CSV, JSON, Parquet, or Excel — max 50MB)</label>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.json,.parquet,.xlsx,.xls"
                className="block w-full text-sm text-text-muted file:mr-3 file:rounded-lg file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-white"
              />
            </div>
            {error && <p className="text-sm text-error">{error}</p>}
            <Button type="submit" disabled={uploading}>
              {uploading ? 'Uploading & profiling…' : 'Upload & profile'}
            </Button>
          </form>
        </Card>
      )}

      {isLoading ? (
        <Skeleton className="h-32" />
      ) : !datasets || datasets.length === 0 ? (
        <EmptyState icon={Database} title="No datasets yet" description="Upload a CSV to see real EDA profiling — missing values, outliers, correlations." />
      ) : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {datasets.map((ds) => (
            <Link key={ds.id} to={`/datasets/${ds.slug}`}>
              <Card className="h-full transition-colors hover:border-primary/50">
                <div className="mb-2 flex items-center justify-between">
                  <Badge tone="primary">{ds.format}</Badge>
                  <Badge tone="neutral">{ds.difficulty}</Badge>
                </div>
                <h2 className="mb-1 font-semibold text-text">{ds.name}</h2>
                <p className="line-clamp-2 text-sm text-text-muted">{ds.description}</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
