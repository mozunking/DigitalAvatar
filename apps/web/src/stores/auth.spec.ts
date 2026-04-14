import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { AUTH_STORAGE_KEYS } from '../api/authStorage'

const loginMock = vi.fn()
const logoutMock = vi.fn()

vi.mock('../api', () => ({
  authApi: {
    login: loginMock,
    logout: logoutMock
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
    logoutMock.mockReset()
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
    expect(localStorage.getItem(AUTH_STORAGE_KEYS.accessToken)).toBe('access-token')
    expect(localStorage.getItem(AUTH_STORAGE_KEYS.refreshToken)).toBe('refresh-token')
  })

  it('revokes refresh token and clears tokens on logout', async () => {
    logoutMock.mockResolvedValue({})

    const { useAuthStore } = await import('./auth')
    const auth = useAuthStore()

    auth.accessToken = 'access-token'
    auth.refreshToken = 'refresh-token'
    auth.user = { id: 'u1', email: 'demo@example.com', display_name: 'Demo User' }
    localStorage.setItem(AUTH_STORAGE_KEYS.accessToken, 'access-token')
    localStorage.setItem(AUTH_STORAGE_KEYS.refreshToken, 'refresh-token')

    await auth.logout()

    expect(logoutMock).toHaveBeenCalledWith('refresh-token')
    expect(auth.isAuthenticated).toBe(false)
    expect(localStorage.getItem(AUTH_STORAGE_KEYS.accessToken)).toBeNull()
    expect(localStorage.getItem(AUTH_STORAGE_KEYS.refreshToken)).toBeNull()
  })

  it('clears local session when logout request fails', async () => {
    logoutMock.mockRejectedValue(new Error('network error'))

    const { useAuthStore } = await import('./auth')
    const auth = useAuthStore()

    auth.accessToken = 'access-token'
    auth.refreshToken = 'refresh-token'
    auth.user = { id: 'u1', email: 'demo@example.com', display_name: 'Demo User' }
    localStorage.setItem(AUTH_STORAGE_KEYS.accessToken, 'access-token')
    localStorage.setItem(AUTH_STORAGE_KEYS.refreshToken, 'refresh-token')

    await auth.logout()

    expect(logoutMock).toHaveBeenCalledWith('refresh-token')
    expect(auth.user).toBeNull()
    expect(localStorage.getItem(AUTH_STORAGE_KEYS.accessToken)).toBeNull()
    expect(localStorage.getItem(AUTH_STORAGE_KEYS.refreshToken)).toBeNull()
  })
})
