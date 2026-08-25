export interface SearchResult {
  type: 'course' | 'lesson' | 'tool' | 'project' | 'resource' | 'glossary_term'
  title: string
  subtitle: string | null
  slug: string | null
  external_url: string | null
}
