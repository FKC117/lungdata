import { Suspense, lazy, useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from 'react-router-dom'
import './App.css'
import './themes.css'
import { fetchCurrentUser, logoutUser, type ApiError, type AuthUser } from './api'
import { LoadingState } from './components/registry-ui'

const PatientSearchPage = lazy(() => import('./pages/PatientSearchPage'))
const PatientDetailPage = lazy(() => import('./pages/PatientDetailPage'))
const PatientEntryPage = lazy(() => import('./pages/PatientEntryPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const LegacyDraftReviewPage = lazy(() => import('./pages/LegacyDraftReviewPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))

function routeAuthenticatedUser(user: AuthUser, navigate: ReturnType<typeof useNavigate>) {
  if (user.default_redirect.startsWith('/admin')) {
    window.location.assign(user.default_redirect)
    return
  }
  navigate(user.default_redirect, { replace: true })
}

function LoginRedirect({ user }: { user: AuthUser }) {
  const navigate = useNavigate()

  useEffect(() => {
    routeAuthenticatedUser(user, navigate)
  }, [navigate, user])

  return (
    <section className="panel">
      <LoadingState label="Redirecting to your workspace" />
    </section>
  )
}

function AppHeader({
  fullName,
  role,
  onLogout,
  isLoggingOut,
  theme,
  onToggleTheme,
}: {
  fullName: string
  role: 'admin' | 'doctor' | 'user'
  onLogout: () => void
  isLoggingOut: boolean
  theme: 'light' | 'dark'
  onToggleTheme: () => void
}) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Lung Cancer Registry</p>
        <h1>Lung Cancer Intelligence Hub</h1>
      </div>
      <div className="topbar-actions">
        <nav className="topnav" aria-label="Primary">
          <NavLink
            to="/patients"
            className={({ isActive }) =>
              isActive ? 'topnav-link topnav-link-active' : 'topnav-link'
            }
          >
            Patients
          </NavLink>
          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              isActive ? 'topnav-link topnav-link-active' : 'topnav-link'
            }
          >
            Analytics
          </NavLink>
          <NavLink
            to="/patients/new"
            className={({ isActive }) =>
              isActive ? 'topnav-link topnav-link-active' : 'topnav-link'
            }
          >
            New Entry
          </NavLink>
          {role === 'admin' ? (
            <NavLink
              to="/legacy-review"
              className={({ isActive }) =>
                isActive ? 'topnav-link topnav-link-active' : 'topnav-link'
              }
            >
              Legacy Review
            </NavLink>
          ) : null}
          {role === 'admin' ? (
            <a className="topnav-link" href="/admin/">
              Django Admin
            </a>
          ) : null}
        </nav>
        <div className="user-badge-cluster">
          <span className="data-pill">
            {role === 'admin' ? 'Registry Admin' : role === 'doctor' ? 'Doctor' : 'User'}
          </span>
          <span className="data-pill">{fullName}</span>
          <button
            type="button"
            className="secondary-button"
            onClick={onLogout}
            disabled={isLoggingOut}
          >
            {isLoggingOut ? 'Signing out...' : 'Logout'}
          </button>
        </div>
        <button
          type="button"
          className={theme === 'dark' ? 'theme-toggle theme-toggle-dark' : 'theme-toggle'}
          onClick={onToggleTheme}
          aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
          title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
        >
          <Sun size={14} aria-hidden="true" />
          <span className="theme-toggle-thumb">{theme === 'dark' ? <Moon size={13} /> : null}</span>
          <Moon size={14} aria-hidden="true" />
        </button>
      </div>
    </header>
  )
}

function ProtectedRoutes({ role }: { role: AuthUser['role'] }) {
  return (
    <Routes>
      <Route index element={<Navigate to="/patients" replace />} />
      <Route path="patients/new" element={<PatientEntryPage />} />
      <Route path="patients/:registryId/edit" element={<PatientEntryPage />} />
      <Route path="patients" element={<PatientSearchPage />} />
      <Route path="analytics" element={<AnalyticsPage />} />
      <Route path="patients/:registryId" element={<PatientDetailPage />} />
      <Route
        path="legacy-review"
        element={role === 'admin' ? <LegacyDraftReviewPage /> : <Navigate to="/patients" replace />}
      />
      <Route path="*" element={<Navigate to="/patients" replace />} />
    </Routes>
  )
}

function App() {
  const location = useLocation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [theme, setTheme] = useState<'light' | 'dark'>(
    () => (window.localStorage.getItem('lung-registry-theme') === 'dark' ? 'dark' : 'light'),
  )

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    window.localStorage.setItem('lung-registry-theme', theme)
  }, [theme])
  const authQuery = useQuery({
    queryKey: ['auth-user'],
    queryFn: fetchCurrentUser,
    retry: false,
  })
  const logoutMutation = useMutation({
    mutationFn: logoutUser,
    onSuccess: async () => {
      queryClient.setQueryData(['auth-user'], null)
      await queryClient.cancelQueries({ queryKey: ['auth-user'] })
      queryClient.removeQueries({ queryKey: ['auth-user'] })
      navigate('/login', { replace: true })
    },
  })

  if (authQuery.isLoading) {
    return (
      <div className="app-shell">
        <main className="page-frame">
          <section className="panel">
            <LoadingState label="Checking session" />
          </section>
        </main>
      </div>
    )
  }

  const authError = authQuery.error as ApiError | null
  const isUnauthenticated = authError?.status === 401 || authError?.status === 403
  const user = isUnauthenticated ? null : authQuery.data ?? null
  const showHeader = Boolean(user) && location.pathname !== '/login'

  return (
    <div className="app-shell">
      {showHeader ? (
        <AppHeader
          fullName={user?.full_name || user?.username || 'User'}
          role={user?.role || 'user'}
          onLogout={() => logoutMutation.mutate()}
          isLoggingOut={logoutMutation.isPending}
          theme={theme}
          onToggleTheme={() => setTheme((current) => (current === 'light' ? 'dark' : 'light'))}
        />
      ) : null}
      <main className="page-frame">
        <Suspense
          fallback={
            <section className="panel">
              <LoadingState label="Loading route" />
            </section>
          }
        >
          <Routes>
            <Route
              path="/login"
              element={
                user ? (
                  <LoginRedirect user={user} />
                ) : (
                  <LoginPage />
                )
              }
            />
            <Route
              path="/*"
              element={
                isUnauthenticated || !user ? (
                  <Navigate
                    to="/login"
                    replace
                    state={{ from: { pathname: location.pathname } }}
                  />
                ) : (
                  <ProtectedRoutes role={user.role} />
                )
              }
            />
          </Routes>
        </Suspense>
      </main>
    </div>
  )
}

export default App
