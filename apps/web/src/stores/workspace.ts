import { defineStore } from 'pinia'
import { agentApi, auditApi, memoryApi, personaApi, taskApi } from '../api'
import type { AgentResponse, AuditLogResponse, MemoryResponse, MemorySummaryResponse, PersonaResponse, TaskResponse } from '../types/generated/api'
import { useAvatarStore } from './avatar'

export const useWorkspaceStore = defineStore('workspace', {
  state: () => ({
    personas: [] as PersonaResponse[],
    agents: [] as AgentResponse[],
    tasks: [] as TaskResponse[],
    memories: [] as MemoryResponse[],
    confirmedMemories: [] as MemorySummaryResponse[],
    auditLogs: [] as AuditLogResponse[],
    loading: false,
    workspaceError: ''
  }),
  actions: {
    async loadAvatarWorkspace(avatarId: string) {
      this.loading = true
      this.workspaceError = ''
      try {
        const [personas, agents, tasks, confirmedMemories] = await Promise.all([
          personaApi.list(avatarId),
          agentApi.list(avatarId),
          taskApi.list(avatarId),
          memoryApi.list('confirmed', avatarId)
        ])
        this.personas = personas.data.items
        this.agents = agents.data.items
        this.tasks = tasks.data.items
        this.confirmedMemories = confirmedMemories.data.items
      } catch {
        this.personas = []
        this.agents = []
        this.tasks = []
        this.confirmedMemories = []
        this.workspaceError = 'workspace_load_failed'
      } finally {
        this.loading = false
      }
    },
    async generatePersona(avatarId: string, samples: string[]) {
      const { data } = await personaApi.generate(avatarId, samples)
      this.personas.unshift(data)
      return data
    },
    async activatePersona(personaId: string, avatarId?: string) {
      const { data } = await personaApi.activate(personaId)
      const avatarStore = useAvatarStore()
      const resolvedAvatarId = avatarId || avatarStore.currentAvatarId
      if (resolvedAvatarId) {
        await this.loadAvatarWorkspace(resolvedAvatarId)
      }
      return data
    },
    async createAgent(avatarId: string, payload: { name: string; role_prompt: string; permissions: string[] }) {
      const { data } = await agentApi.create(avatarId, payload)
      this.agents.unshift(data)
      return data
    },
    async updateAgentStatus(agentId: string, status: 'ready' | 'disabled') {
      const { data } = await agentApi.updateStatus(agentId, status)
      const index = this.agents.findIndex((item) => item.id === agentId)
      if (index >= 0) {
        this.agents[index] = data
      }
      return data
    },
    async runTask(payload: { avatar_id: string; agent_id: string; input: string }) {
      const { data } = await taskApi.create(payload)
      this.tasks.unshift(data)
      return data
    },
    async loadPendingMemories() {
      const avatarStore = useAvatarStore()
      const avatarId = avatarStore.currentAvatarId
      if (!avatarId) return
      try {
        const { data } = await memoryApi.pending(avatarId)
        this.memories = data.items
      } catch {
        this.memories = []
        this.workspaceError = 'workspace_load_failed'
      }
    },
    async loadConfirmedMemories(avatarId?: string) {
      const avatarStore = useAvatarStore()
      const resolvedAvatarId = avatarId || avatarStore.currentAvatarId
      if (!resolvedAvatarId) return
      try {
        const { data } = await memoryApi.list('confirmed', resolvedAvatarId)
        this.confirmedMemories = data.items
      } catch {
        this.confirmedMemories = []
        this.workspaceError = 'workspace_load_failed'
      }
    },
    async searchMemories(avatarId: string, query?: string, type?: string) {
      const { data } = await memoryApi.search(avatarId, query, type)
      return data.items
    },
    async getMemoryDetail(avatarId: string, memoryId: string) {
      const { data } = await memoryApi.getByAvatar(avatarId, memoryId)
      return data
    },
    async confirmMemory(memoryId: string, reason?: string) {
      const { data } = await memoryApi.confirm(memoryId, reason)
      this.memories = this.memories.filter((item) => item.id !== memoryId)
      this.confirmedMemories.unshift({
        id: data.id,
        avatar_id: data.avatar_id,
        task_id: data.task_id,
        type: data.type,
        sensitivity: data.sensitivity,
        state: data.state,
        excerpt: data.content.slice(0, 120),
        source_type: data.source_type,
        created_at: data.created_at,
      })
    },
    async rejectMemory(memoryId: string, reason?: string) {
      await memoryApi.reject(memoryId, reason)
      this.memories = this.memories.filter((item) => item.id !== memoryId)
    },
    async loadAuditLogs(params?: { trace_id?: string; resource_type?: string; start_at?: string; end_at?: string }) {
      const { data } = await auditApi.list(params)
      this.auditLogs = data.items
    }
  }
})

