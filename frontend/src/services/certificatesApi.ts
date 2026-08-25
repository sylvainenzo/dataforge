import { api } from '@/lib/api'
import type { Certificate, CertificateVerification } from '@/types/certificates'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const certificatesApi = {
  list: () => api.get<Certificate[]>('/api/v1/certificates'),
  issue: (courseSlug: string) => api.post<Certificate>(`/api/v1/courses/${courseSlug}/certificate`),
  downloadUrl: (certificateId: string) => `${API_BASE_URL}/api/v1/certificates/${certificateId}/download`,
  verify: (certificateNumber: string) =>
    api.get<CertificateVerification>(`/api/v1/certificates/verify/${certificateNumber}`),
}
