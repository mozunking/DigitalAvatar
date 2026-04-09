import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const loginMock = vi.fn()

vi.mock('../api', () => ({
  authApi: {
    login: loginMock
  }
}))

const storage = new Map<string, string>()
const localStorageMock = {
  getItem: (key: string) => storage.get(key) ?? null,
  setItem: (key: string, value: string) => {
    storage.set(key, value)
  },
  removeItem: (key: string) => {
    storage.delete(key)
  }
}

Object.defineProperty(globalThis, 'localStorage', {
  value: localStorageMock,
  configurable: true
})

describe('auth store', () => {
  beforeEach(() => {
    storage.clear()
    loginMock.mockReset()
    setActivePinia(createPinia())
  })

  it('stores login tokens after successful login', async () => {
    loginMock.mockResolvedValue({
      data: {
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        user: { id: 'u1', email: 'demo@example.com', display_name: 'Demo User' },
        trace_id: 'trace-1'
      }
    })

    const { useAuthStore } = await import('./auth')
    const auth = useAuthStore()

    await auth.login('demo@example.com', 'demo123456')

    expect(auth.isAuthenticated).toBe(true)
    expect(localStorage.getItem('digital-avatar-access-token')).toBe('access-token')
    expect(localStorage.getItem('digital-avatar-refresh-token')).toBe('refresh-token')
  })

  it('clears tokens on logout', async () => {
    const { useAuthStore } = await import('./auth')
    const auth = useAuthStore()

    auth.accessToken = 'access-token'
    auth.refreshToken = 'refresh-token'
    auth.user = { id: 'u1', email: 'demo@example.com', display_name: 'Demo User' }
    localStorage.setItem('digital-avatar-access-token', 'access-token')
    localStorage.setItem('digital-avatar-refresh-token', 'refresh-token')

    auth.logout()

    expect(auth.isAuthenticated).toBe(false)
    expect(localStorage.getItem('digital-avatar-access-token')).toBeNull()
    expect(localStorage.getItem('digital-avatar-refresh-token')).toBeNull()
  })
})
