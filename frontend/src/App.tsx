import { RouterProvider } from 'react-router-dom'
import { QueryProvider } from '@/app/QueryProvider'
import { LanguageSync } from '@/app/LanguageSync'
import { ThemeSync } from '@/app/ThemeSync'
import { router } from '@/routes/router'

export default function App() {
  return (
    <QueryProvider>
      <ThemeSync />
      <LanguageSync />
      <RouterProvider router={router} />
    </QueryProvider>
  )
}
