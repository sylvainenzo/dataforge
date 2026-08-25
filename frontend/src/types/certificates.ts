export interface Certificate {
  id: string
  course_id: string | null
  learning_path_id: string | null
  title: string
  certificate_number: string
  issued_at: string
}

export interface CertificateVerification {
  certificate_number: string
  recipient_name: string
  course_title: string
  issued_at: string
}
