import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const personaListMock = vi.fn()
const personaActivateMock = vi.fn()
const agentListMock = vi.fn()
const taskListMock = vi.fn()
const memoryListMock = vi.fn()
const memoryPendingMock = vi.fn()

vi.mock('../api', () => ({
  personaApi: {
    list: personaListMock,
    activate: personaActivateMock,
  },
  agentApi: {
    list: agentListMock,
  },
  taskApi: {
    list: taskListMock,
  },
  memoryApi: {
    list: memoryListMock,
    pending: memoryPendingMock,
    confirm: vi.fn(),
    reject: vi.fn(),
    search: vi.fn(),
    getByAvatar: vi.fn(),
  },
  auditApi: {
    list: vi.fn(),
  },
}))

describe('workspace store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    personaListMock.mockReset()
    personaActivateMock.mockReset()
    agentListMock.mockReset()
    taskListMock.mockReset()
    memoryListMock.mockReset()
    memoryPendingMock.mockReset()
  })

  it('stores confirmed memories when workspace load succeeds', async () => {
    personaListMock.mockResolvedValue({ data: { items: [{ id: 'p1', avatar_id: 'a1', summary: 'sum', source_count: 1, version: 2, is_current: true, created_at: '2026-04-09T10:00:00Z' }] } })
    agentListMock.mockResolvedValue({ data: { items: [{ id: 'g1', avatar_id: 'a1', name: 'agent', role_prompt: 'role', permissions: [], status: 'ready', created_at: '2026-04-09T10:00:00Z' }] } })
    taskListMock.mockResolvedValue({ data: { items: [{ task_id: 't1', status: 'succeeded', trace_id: 'trace-1', result: 'done', error: null, created_at: '2026-04-09T10:00:00Z' }] } })
    memoryListMock.mockResolvedValue({ data: { items: [{ id: 'm1', avatar_id: 'a1', task_id: 't1', type: 'preference', sensitivity: 'medium', state: 'confirmed', excerpt: 'Prefers short answers', source_type: 'task', created_at: '2026-04-09T10:00:00Z' }] } })

    const { useWorkspaceStore } = await import('./workspace')
    const workspace = useWorkspaceStore()

    await workspace.loadAvatarWorkspace('a1')

    expect(workspace.workspaceError).toBe('')
    expect(workspace.confirmedMemories).toHaveLength(1)
    expect(workspace.confirmedMemories[0].state).toBe('confirmed')
    expect(workspace.confirmedMemories[0].excerpt).toBe('Prefers short answers')
  })

  it('reloads workspace for explicit avatar when activating persona from avatar route', async () => {
    personaActivateMock.mockResolvedValue({ data: { id: 'p2', avatar_id: 'a2', summary: 'sum', source_count: 1, version: 3, is_current: true, created_at: '2026-04-09T10:00:00Z' } })
    personaListMock.mockResolvedValue({ data: { items: [] } })
    agentListMock.mockResolvedValue({ data: { items: [] } })
    taskListMock.mockResolvedValue({ data: { items: [] } })
    memoryListMock.mockResolvedValue({ data: { items: [] } })

    const { useWorkspaceStore } = await import('./workspace')
    const workspace = useWorkspaceStore()

    await workspace.activatePersona('p2', 'a2')

    expect(personaActivateMock).toHaveBeenCalledWith('p2')
    expect(personaListMock).toHaveBeenCalledWith('a2')
    expect(agentListMock).toHaveBeenCalledWith('a2')
    expect(taskListMock).toHaveBeenCalledWith('a2')
    expect(memoryListMock).toHaveBeenCalledWith('confirmed', 'a2')
  })

})
