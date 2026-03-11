import { useEffect } from 'react'
import { useAuth } from './auth/AuthContext'
import { useRouter } from './router'
import { getDefaultAuthenticatedPath, routes } from './routes'

function RouteGateSkeleton({ message = 'Загрузка сессии...' }) {
  return (
    <main className="route-state-shell">
      <div className="route-state-card">
        <div className="route-state-spinner" aria-hidden="true" />
        <p>{message}</p>
      </div>
    </main>
  )
}

export function ProtectedRoute({
  children,
  redirectTo = routes.login,
  roles = null,
  requireVerifiedDoctor = false,
}) {
  const auth = useAuth()
  const { location, navigate } = useRouter()

  const isMissingRole = roles?.length ? !auth.hasRole(...roles) : false
  const isMissingDoctorVerification = requireVerifiedDoctor && !auth.isVerifiedDoctor

  useEffect(() => {
    if (!auth.isReady) {
      return
    }

    if (!auth.isAuthenticated) {
      const returnTo = encodeURIComponent(`${location.pathname}${location.search}${location.hash || ''}`)
      navigate(`${redirectTo}?returnTo=${returnTo}`, { replace: true })
      return
    }

    if (isMissingRole || isMissingDoctorVerification) {
      navigate(`${getDefaultAuthenticatedPath(auth.user)}?access=denied`, { replace: true })
    }
  }, [
    auth.isAuthenticated,
    auth.isReady,
    auth.user,
    isMissingDoctorVerification,
    isMissingRole,
    location.hash,
    location.pathname,
    location.search,
    navigate,
    redirectTo,
  ])

  if (!auth.isReady) {
    return <RouteGateSkeleton />
  }

  if (!auth.isAuthenticated || isMissingRole || isMissingDoctorVerification) {
    return <RouteGateSkeleton message="Проверяем доступ..." />
  }

  return children
}

export function GuestOnlyRoute({ children, redirectTo = null }) {
  const auth = useAuth()
  const { navigate } = useRouter()

  useEffect(() => {
    if (auth.isReady && auth.isAuthenticated) {
      navigate(redirectTo || getDefaultAuthenticatedPath(auth.user), { replace: true })
    }
  }, [auth.isAuthenticated, auth.isReady, auth.user, navigate, redirectTo])

  if (!auth.isReady) {
    return <RouteGateSkeleton />
  }

  if (auth.isAuthenticated) {
    return <RouteGateSkeleton message="Перенаправляем в кабинет..." />
  }

  return children
}
