import { describe, expect, it } from 'vitest'
import { resolveRouteRedirect } from '../../apps/web/src/router/guard'

describe('web route guard', () => {
  it('redirects anonymous users away from protected routes', () => {
    expect(resolveRouteRedirect({ path: '/dashboard', meta: { requiresAuth: true } }, false)).toBe('/login')
    expect(resolveRouteRedirect({ path: '/avatars/avatar-1/persona', meta: { requiresAuth: true } }, false)).toBe('/login')
    expect(resolveRouteRedirect({ path: '/avatars/avatar-1/agents', meta: { requiresAuth: true } }, false)).toBe('/login')
    expect(resolveRouteRedirect({ path: '/memories/pending', meta: { requiresAuth: true } }, false)).toBe('/login')
  })

  it('redirects authenticated users away from the login page', () => {
    expect(resolveRouteRedirect({ path: '/login' }, true)).toBe('/dashboard')
  })

  it('allows public or already-authorized navigation', () => {
    expect(resolveRouteRedirect({ path: '/dashboard', meta: { requiresAuth: true } }, true)).toBe(true)
    expect(resolveRouteRedirect({ path: '/avatars/avatar-1/persona', meta: { requiresAuth: true } }, true)).toBe(true)
    expect(resolveRouteRedirect({ path: '/avatars/avatar-1/agents', meta: { requiresAuth: true } }, true)).toBe(true)
    expect(resolveRouteRedirect({ path: '/memories/pending', meta: { requiresAuth: true } }, true)).toBe(true)
    expect(resolveRouteRedirect({ path: '/login' }, false)).toBe(true)
    expect(resolveRouteRedirect({ path: '/settings', meta: {} }, false)).toBe(true)
  })
})
