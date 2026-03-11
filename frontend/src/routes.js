export const routes = Object.freeze({
  landing: '/',
  login: '/login-desktop-ru',
  loginAlias: '/login',
  register: '/registration-desktop-ru',
  registerAlias: '/register',
  doctors: '/doctor-directory-with-filters-ru',
  doctorsAlias: '/doctors',
  doctorProfile: '/doctor-public-profile-ru',
  questions: '/public-questions-feed-ru',
  questionsAlias: '/questions',
  questionDetail: '/public-question-detail-ru',
  questionDetailAlias: '/question',
  account: '/account',
  profileAlias: '/profile',
  admin: '/admin-doctor-moderation',
  adminAlias: '/admin',
  notFound: '/404',
})

export function getDefaultAuthenticatedPath(user) {
  if (user?.role === 'admin' || user?.role === 'superuser') {
    return routes.admin
  }

  return routes.account
}

export function resolveSafeAppPath(value, fallback = routes.landing) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//')) {
    return fallback
  }

  if (value.startsWith('/api')) {
    return fallback
  }

  return value
}

export function withReturnTo(path, returnTo) {
  const safeReturnTo = resolveSafeAppPath(returnTo, '')

  if (!safeReturnTo) {
    return path
  }

  const searchParams = new URLSearchParams()
  searchParams.set('returnTo', safeReturnTo)

  return `${path}?${searchParams.toString()}`
}
