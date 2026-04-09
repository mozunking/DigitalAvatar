import api from './client'
import type {
  AgentResponse,
  AuditLogResponse,
  AvatarResponse,
  LoginResponse,
  MemoryResponse,
  PaginatedResponse,
  PersonaResponse,
  TaskResponse
} from '../types/generated/api'

export type ApiError = {
  error?: {
    code: string
    message: string
    trace_id: string
    details?: Record<string, unknown>
  }
}

export const authApi = {
  login: (email: string, password: string) => api.post<LoginResponse>('/auth/login', { email, password }),
  register: (email: string, password: string, displayName?: string) =>
    api.post<LoginResponse>('/auth/register', { email, password, display_name: displayName }),
  me: () => api.get('/auth/me'),
  refresh: (refreshToken: string) => api.post<LoginResponse>('/auth/refresh', { refresh_token: refreshToken }),
}

export const avatarApi = {
  list: (page = 1, pageSize = 20) => api.get<PaginatedResponse<AvatarResponse>>('/avatars', { params: { page, page_size: pageSize } }),
  get: (avatarId: string) => api.get<AvatarResponse>(`/avatars/${avatarId}`),
  create: (payload: { name: string; goal: string; visibility: string }) => api.post<AvatarResponse>('/avatars', payload),
  update: (avatarId: string, payload: { name: string; goal: string; visibility: string }) => api.put<AvatarResponse>(`/avatars/${avatarId}`, payload),
}

export const personaApi = {
  list: (avatarId: string, page = 1, pageSize = 20) => api.get<PaginatedResponse<PersonaResponse>>(`/avatars/${avatarId}/personas`, { params: { page, page_size: pageSize } }),
  latest: (avatarId: string) => api.get<PersonaResponse>(`/avatars/${avatarId}/persona/latest`),
  generate: (avatarId: string, samples: string[]) => api.post<PersonaResponse>(`/avatars/${avatarId}/persona/generate`, { samples }),
  activate: (personaId: string) => api.post<PersonaResponse>(`/personas/${personaId}/activate`),
}

export const agentApi = {
  list: (avatarId: string, page = 1, pageSize = 20) => api.get<PaginatedResponse<AgentResponse>>(`/avatars/${avatarId}/agents`, { params: { page, page_size: pageSize } }),
  get: (avatarId: string, agentId: string) => api.get<AgentResponse>(`/avatars/${avatarId}/agents/${agentId}`),
  create: (avatarId: string, payload: { name: string; role_prompt: string; permissions: string[] }) =>
    api.post<AgentResponse>(`/avatars/${avatarId}/agents`, payload),
  updateStatus: (avatarId: string, agentId: string, status: 'ready' | 'disabled') =>
    api.patch<AgentResponse>(`/avatars/${avatarId}/agents/${agentId}`, { status }),
}

export const taskApi = {
  list: (avatarId?: string) => api.get<PaginatedResponse<TaskResponse>>('/tasks', { params: avatarId ? { avatar_id: avatarId } : {} }),
  create: (payload: { avatar_id: string; agent_id: string; input: string; trace_id?: string }) => api.post<TaskResponse>('/tasks', payload),
  get: (taskId: string) => api.get<TaskResponse>(`/tasks/${taskId}`),
}

export const memoryApi = {
  list: (state?: string, avatarId?: string) => api.get<PaginatedResponse<MemoryResponse>>('/memories', { params: { ...(state ? { state } : {}), ...(avatarId ? { avatar_id: avatarId } : {}) } }),
  get: (memoryId: string) => api.get<MemoryResponse>(`/memories/${memoryId}`),
  search: (avatarId: string, query?: string, type?: string) => api.get<PaginatedResponse<MemoryResponse>>(`/avatars/${avatarId}/memories/search`, { params: { ...(query ? { query } : {}), ...(type ? { type } : {}) } }),
  pending: (avatarId: string) => api.get<PaginatedResponse<MemoryResponse>>(`/avatars/${avatarId}/memories/pending`),
  confirm: (memoryId: string, reason?: string) => api.post<MemoryResponse>(`/memories/${memoryId}/confirm`, { reason }),
  reject: (memoryId: string, reason?: string) => api.post<MemoryResponse>(`/memories/${memoryId}/reject`, { reason }),
  archive: (memoryId: string, reason?: string) => api.post<MemoryResponse>(`/memories/${memoryId}/archive`, { reason }),
}

export const auditApi = {
  list: (params?: { trace_id?: string; resource_type?: string; start_at?: string; end_at?: string; page?: number; page_size?: number }) =>
    api.get<PaginatedResponse<AuditLogResponse>>('/audit', { params }),
  get: (auditId: string) => api.get<AuditLogResponse>(`/audit/${auditId}`),
}
