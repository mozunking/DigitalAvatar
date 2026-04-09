import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

// Mock the API module
vi.mock('../../src/api', () => ({
  authApi: {
    login: vi.fn().mockResolvedValue({ data: { access_token: 'at', refresh_token: 'rt', user: { id: '1', email: 'test@test.com', display_name: 'Test' }, trace_id: 't1' } }),
    register: vi.fn(),
    me: vi.fn(),
    refresh: vi.fn(),
  },
  avatarApi: {
    list: vi.fn().mockResolvedValue({ data: { items: [], page: 1, page_size: 20, total: 0 } }),
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
  personaApi: {
    list: vi.fn().mockResolvedValue({ data: { items: [], page: 1, page_size: 20, total: 0 } }),
    generate: vi.fn(),
    activate: vi.fn(),
  },
  agentApi: {
    list: vi.fn().mockResolvedValue({ data: { items: [], page: 1, page_size: 20, total: 0 } }),
    create: vi.fn(),
    updateStatus: vi.fn(),
  },
  taskApi: {
    list: vi.fn().mockResolvedValue({ data: { items: [], page: 1, page_size: 20, total: 0 } }),
    create: vi.fn(),
    get: vi.fn(),
  },
  memoryApi: {
    list: vi.fn().mockResolvedValue({ data: { items: [], page: 1, page_size: 20, total: 0 } }),
    search: vi.fn(),
    pending: vi.fn().mockResolvedValue({ data: { items: [], page: 1, page_size: 20, total: 0 } }),
    confirm: vi.fn(),
    reject: vi.fn(),
  },
  auditApi: {
    list: vi.fn().mockResolvedValue({ data: { items: [], page: 1, page_size: 20, total: 0 } }),
  },
}))

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with unauthenticated state', () => {
    const { useAuthStore } = await import('../../src/stores/auth')
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
    expect(store.accessToken).toBe('')
  })

  it('sets authenticated after login', async () => {
    const { useAuthStore } = await import('../../src/stores/auth')
    const store = useAuthStore()
    await store.login('test@test.com', 'password')
    expect(store.isAuthenticated).toBe(true)
    expect(store.accessToken).toBe('at')
  })
})

describe('useWorkspaceStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with empty state', () => {
    const { useWorkspaceStore } = await import('../../src/stores/workspace')
    const store = useWorkspaceStore()
    expect(store.personas).toEqual([])
    expect(store.agents).toEqual([])
    expect(store.tasks).toEqual([])
  })
})
