import { describe, expect, it } from 'vitest'
import { DEMO_AVATAR_GOAL, DEMO_AVATAR_NAME, getOnboardingStorageKey, isOnboardingReadyToFinish } from './onboarding'

describe('onboarding helpers', () => {
  it('builds a stable storage key per user and avatar', () => {
    expect(getOnboardingStorageKey('u1', 'a1')).toBe('digital-avatar-onboarding:u1:a1')
    expect(getOnboardingStorageKey('u1')).toBe('digital-avatar-onboarding:u1:none')
  })

  it('marks onboarding finishable only after the full loop is complete', () => {
    expect(isOnboardingReadyToFinish({
      hasAvatar: true,
      hasPersona: true,
      hasAgent: true,
      hasTask: true,
      pendingMemories: 1,
      confirmedMemories: 0,
    })).toBe(true)

    expect(isOnboardingReadyToFinish({
      hasAvatar: true,
      hasPersona: true,
      hasAgent: false,
      hasTask: true,
      pendingMemories: 1,
      confirmedMemories: 0,
    })).toBe(false)

    expect(isOnboardingReadyToFinish({
      hasAvatar: true,
      hasPersona: true,
      hasAgent: true,
      hasTask: true,
      pendingMemories: 0,
      confirmedMemories: 0,
    })).toBe(false)
  })

  it('keeps demo avatar seed constants aligned with the dashboard flow', () => {
    expect(DEMO_AVATAR_NAME).toBe('Demo Avatar')
    expect(DEMO_AVATAR_GOAL).toContain('digital identity')
  })
})
