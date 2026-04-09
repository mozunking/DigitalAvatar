export type { components, operations, paths, webhooks, $defs } from './openapi'

import type { components } from './openapi'

type Schemas = components['schemas']

export type AgentResponse = Schemas['AgentResponse']
export type AuditLogResponse = Schemas['AuditLogResponse']
export type AvatarResponse = Schemas['AvatarResponse']
export type LoginResponse = Schemas['LoginResponse']
export type MemoryResponse = Schemas['MemoryResponse']
export type PersonaResponse = Schemas['PersonaResponse']
export type TaskResponse = Schemas['TaskResponse']
export type UserResponse = Schemas['UserResponse']

export type PaginatedResponse<T> = Omit<Schemas['PaginatedResponse'], 'items'> & {
  items: T[]
}
