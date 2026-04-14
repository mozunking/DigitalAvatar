export type ProviderHealth = {
  mode: string
  status: string
  model: string
  version: string
  url: string
  chatModelAvailable: boolean
  message: string
}

const DEFAULT_OLLAMA_URL = 'http://localhost:11434'

export const normalizeProviderHealth = (payload?: Record<string, unknown> | null): ProviderHealth => ({
  mode: typeof payload?.mode === 'string' && payload.mode ? payload.mode : 'mock',
  status: typeof payload?.status === 'string' && payload.status ? payload.status : 'degraded',
  model: typeof payload?.model === 'string' ? payload.model : '',
  version: typeof payload?.version === 'string' && payload.version ? payload.version : 'unknown',
  url: typeof payload?.base_url === 'string' && payload.base_url ? payload.base_url : DEFAULT_OLLAMA_URL,
  chatModelAvailable: typeof payload?.chat_model_available === 'boolean' ? payload.chat_model_available : false,
  message: typeof payload?.message === 'string' ? payload.message : '',
})

export const providerModeLabelKey = (mode: string) => (mode === 'live' ? 'settings.ollamaOnline' : 'settings.ollamaMock')

export const providerStatusLabelKey = (status: string) => {
  if (status === 'ok') return 'settings.providerReady'
  if (status === 'mock') return 'settings.providerMockMode'
  return 'settings.providerDegraded'
}

export const providerTagType = (health: ProviderHealth) => {
  if (health.status === 'ok' && health.mode === 'live') return 'success'
  if (health.status === 'mock' || health.mode !== 'live') return 'warning'
  return 'danger'
}
