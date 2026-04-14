export const resolveRouteRedirect = (to: { path: string; meta?: { requiresAuth?: boolean } }, isAuthenticated: boolean) => {
  if (to.meta?.requiresAuth && !isAuthenticated) {
    return '/login'
  }
  if (to.path === '/login' && isAuthenticated) {
    return '/dashboard'
  }
  return true
}
