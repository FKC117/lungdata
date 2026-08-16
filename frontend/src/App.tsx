import { Suspense, lazy, useEffect } from 'react'
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
import { fetchCurrentUser, logoutUser, type ApiError, type AuthUser } from './api'
import { LoadingState } from './components/registry-ui'

const PatientSearchPage = lazy(() => import('./pages/PatientSearchPage'))
const PatientDetailPage = lazy(() => import('./pages/PatientDetailPage'))
const PatientEntryPage = lazy(() => import('./pages/PatientEntryPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))

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
}: {
  fullName: string
  role: 'admin' | 'doctor' | 'user'
  onLogout: () => void
  isLoggingOut: boolean
}) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Canonical Registry</p>
        <h1>Lung Panel Intelligence Hub</h1>
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
            to="/patients/new"
            className={({ isActive }) =>
              isActive ? 'topnav-link topnav-link-active' : 'topnav-link'
            }
          >
            New Entry
          </NavLink>
          {role === 'admin' ? (
            <a className="topnav-link" href="/admin/">
              Admin Console
            </a>
          ) : null}
        </nav>
        <div className="user-badge-cluster">
          <span className="data-pill">
            {role === 'admin' ? 'Admin' : role === 'doctor' ? 'Doctor' : 'User'}
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
      </div>
    </header>
  )
}

function ProtectedRoutes() {
  return (
    <Routes>
      <Route index element={<Navigate to="/patients" replace />} />
      <Route path="patients/new" element={<PatientEntryPage />} />
      <Route path="patients" element={<PatientSearchPage />} />
      <Route path="patients/:registryId" element={<PatientDetailPage />} />
      <Route path="*" element={<Navigate to="/patients" replace />} />
    </Routes>
  )
}

function App() {
  const location = useLocation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const authQuery = useQuery({
    queryKey: ['auth-user'],
    queryFn: fetchCurrentUser,
    retry: false,
  })
  const logoutMutation = useMutation({
    mutationFn: logoutUser,
    onSettled: async () => {
      await queryClient.invalidateQueries({ queryKey: ['auth-user'] })
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
  const isUnauthenticated = authError?.status === 401
  const user = authQuery.data ?? null
  const showHeader = Boolean(user) && location.pathname !== '/login'

  return (
    <div className="app-shell">
      {showHeader ? (
        <AppHeader
          fullName={user?.full_name || user?.username || 'User'}
          role={user?.role || 'user'}
          onLogout={() => logoutMutation.mutate()}
          isLoggingOut={logoutMutation.isPending}
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
                  <ProtectedRoutes />
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
