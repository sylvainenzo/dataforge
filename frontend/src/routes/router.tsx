import { Compass } from 'lucide-react'
import { lazy } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import { LoginPage } from '@/features/auth/LoginPage'
import { RegisterPage } from '@/features/auth/RegisterPage'
import { AppLayout } from '@/layouts/AppLayout'
import { ComingSoonPage } from '@/pages/ComingSoonPage'
import { RequireAuth } from '@/routes/RequireAuth'
import { RequireRole } from '@/routes/RequireRole'

// Route-level code splitting (Phase 1 §54: "do not load the entire
// curriculum into the browser at once") — everything reachable only after
// sign-in loads on demand instead of bloating the initial bundle. Login/
// Register stay eager since they're the very first thing an unauthenticated
// visitor needs; lazy-loading them would just add a round-trip before the
// sign-in form even appears.
const DashboardPage = lazy(() => import('@/features/dashboard/DashboardPage').then((m) => ({ default: m.DashboardPage })))
const CoursesPage = lazy(() => import('@/features/curriculum/CoursesPage').then((m) => ({ default: m.CoursesPage })))
const CourseDetailPage = lazy(() =>
  import('@/features/curriculum/CourseDetailPage').then((m) => ({ default: m.CourseDetailPage })),
)
const LessonPage = lazy(() => import('@/features/curriculum/LessonPage').then((m) => ({ default: m.LessonPage })))
const LearningPathsPage = lazy(() =>
  import('@/features/curriculum/LearningPathsPage').then((m) => ({ default: m.LearningPathsPage })),
)
const LearningPathDetailPage = lazy(() =>
  import('@/features/curriculum/LearningPathDetailPage').then((m) => ({ default: m.LearningPathDetailPage })),
)
const LabsIndexPage = lazy(() => import('@/features/labs/LabsIndexPage').then((m) => ({ default: m.LabsIndexPage })))
const PythonLabPage = lazy(() => import('@/features/labs/PythonLabPage').then((m) => ({ default: m.PythonLabPage })))
const SqlLabPage = lazy(() => import('@/features/labs/SqlLabPage').then((m) => ({ default: m.SqlLabPage })))
const RLabPage = lazy(() => import('@/features/labs/RLabPage').then((m) => ({ default: m.RLabPage })))
const StatsLabPage = lazy(() => import('@/features/labs/StatsLabPage').then((m) => ({ default: m.StatsLabPage })))
const DataVizLabPage = lazy(() => import('@/features/labs/DataVizLabPage').then((m) => ({ default: m.DataVizLabPage })))
const ProjectsPage = lazy(() => import('@/features/projects/ProjectsPage').then((m) => ({ default: m.ProjectsPage })))
const ProjectDetailPage = lazy(() =>
  import('@/features/projects/ProjectDetailPage').then((m) => ({ default: m.ProjectDetailPage })),
)
const DatasetsPage = lazy(() => import('@/features/datasets/DatasetsPage').then((m) => ({ default: m.DatasetsPage })))
const DatasetDetailPage = lazy(() =>
  import('@/features/datasets/DatasetDetailPage').then((m) => ({ default: m.DatasetDetailPage })),
)
const FlashcardsPage = lazy(() => import('@/features/flashcards/FlashcardsPage').then((m) => ({ default: m.FlashcardsPage })))
const MacSetupPage = lazy(() => import('@/features/mac-setup/MacSetupPage').then((m) => ({ default: m.MacSetupPage })))
const ToolDetailPage = lazy(() => import('@/features/mac-setup/ToolDetailPage').then((m) => ({ default: m.ToolDetailPage })))
const AdminPage = lazy(() => import('@/features/admin/AdminPage').then((m) => ({ default: m.AdminPage })))
const ResourcesPage = lazy(() => import('@/features/resources/ResourcesPage').then((m) => ({ default: m.ResourcesPage })))
const CareerPage = lazy(() => import('@/features/career/CareerPage').then((m) => ({ default: m.CareerPage })))
const InterviewQuestionsPage = lazy(() =>
  import('@/features/interview/InterviewQuestionsPage').then((m) => ({ default: m.InterviewQuestionsPage })),
)
const SettingsPage = lazy(() => import('@/features/settings/SettingsPage').then((m) => ({ default: m.SettingsPage })))
const CertificatesPage = lazy(() =>
  import('@/features/certificates/CertificatesPage').then((m) => ({ default: m.CertificatesPage })),
)
const CertificateVerifyPage = lazy(() =>
  import('@/features/certificates/CertificateVerifyPage').then((m) => ({ default: m.CertificateVerifyPage })),
)
const PublicPortfolioPage = lazy(() =>
  import('@/features/portfolio/PublicPortfolioPage').then((m) => ({ default: m.PublicPortfolioPage })),
)

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '/certificates/verify', element: <CertificateVerifyPage /> },
  { path: '/certificates/verify/:certificateNumber', element: <CertificateVerifyPage /> },
  { path: '/portfolio/:userId', element: <PublicPortfolioPage /> },
  {
    path: '/',
    element: (
      <RequireAuth>
        <AppLayout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'courses', element: <CoursesPage /> },
      { path: 'courses/:slug', element: <CourseDetailPage /> },
      { path: 'lessons/:slug', element: <LessonPage /> },
      { path: 'learning-paths', element: <LearningPathsPage /> },
      { path: 'learning-paths/:slug', element: <LearningPathDetailPage /> },
      { path: 'labs', element: <LabsIndexPage /> },
      { path: 'labs/python', element: <PythonLabPage /> },
      { path: 'labs/sql', element: <SqlLabPage /> },
      { path: 'labs/r', element: <RLabPage /> },
      { path: 'labs/statistics', element: <StatsLabPage /> },
      { path: 'labs/data-viz', element: <DataVizLabPage /> },
      { path: 'projects', element: <ProjectsPage /> },
      { path: 'projects/:slug', element: <ProjectDetailPage /> },
      { path: 'datasets', element: <DatasetsPage /> },
      { path: 'datasets/:slug', element: <DatasetDetailPage /> },
      { path: 'flashcards', element: <FlashcardsPage /> },
      { path: 'resources', element: <ResourcesPage /> },
      { path: 'career', element: <CareerPage /> },
      { path: 'interview-questions', element: <InterviewQuestionsPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'certificates', element: <CertificatesPage /> },
      { path: 'mac-setup', element: <MacSetupPage /> },
      { path: 'tools/:slug', element: <ToolDetailPage /> },
      {
        path: 'admin',
        element: (
          <RequireRole role="admin">
            <AdminPage />
          </RequireRole>
        ),
      },
      {
        path: '*',
        element: (
          <ComingSoonPage icon={Compass} title="Nothing here yet" description="This page doesn't exist yet — check the sidebar for what's built so far." />
        ),
      },
    ],
  },
])
