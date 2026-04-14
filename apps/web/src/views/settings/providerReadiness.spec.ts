import { describe, expect, it } from 'vitest'

import {
  normalizeProviderHealth,
  providerModeLabelKey,
  providerStatusLabelKey,
  providerTagType,
} from './providerReadiness'

describe('provider readiness helpers', () => {
  it('normalizes provider health payload with backend diagnostics', () => {
    const health = normalizeProviderHealth({
      mode: 'live',
      status: 'degraded',
      model: 'qwen3.5:latest',
      version: '0.1.28',
      base_url: 'http://ollama:11434',
      chat_model_available: false,
      message: 'No chat-capable Ollama model available.',
    })

    expect(health).toEqual({
      mode: 'live',
      status: 'degraded',
      model: 'qwen3.5:latest',
      version: '0.1.28',
      url: 'http://ollama:11434',
      chatModelAvailable: false,
      message: 'No chat-capable Ollama model available.',
    })
  })

  it('falls back to conservative defaults when payload is missing', () => {
    const health = normalizeProviderHealth(undefined)

    expect(health).toEqual({
      mode: 'mock',
      status: 'degraded',
      model: '',
      version: 'unknown',
      url: 'http://localhost:11434',
      chatModelAvailable: false,
      message: '',
    })
  })

  it('derives provider labels and tag state for live, mock, and degraded modes', () => {
    expect(providerModeLabelKey('live')).toBe('settings.ollamaOnline')
    expect(providerModeLabelKey('mock')).toBe('settings.ollamaMock')
    expect(providerStatusLabelKey('ok')).toBe('settings.providerReady')
    expect(providerStatusLabelKey('mock')).toBe('settings.providerMockMode')
    expect(providerStatusLabelKey('degraded')).toBe('settings.providerDegraded')

    expect(providerTagType(normalizeProviderHealth({ mode: 'live', status: 'ok' }))).toBe('success')
    expect(providerTagType(normalizeProviderHealth({ mode: 'mock', status: 'mock' }))).toBe('warning')
    expect(providerTagType(normalizeProviderHealth({ mode: 'live', status: 'degraded' }))).toBe('danger')
  })
})
