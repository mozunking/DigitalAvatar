export const DEMO_AVATAR_NAME = 'Demo Avatar'
export const DEMO_AVATAR_GOAL = 'Help manage a digital identity and complete safe tasks.'

export const getOnboardingStorageKey = (userId: string, avatarId?: string) => {
  const resolvedAvatarId = avatarId || 'none'
  return `digital-avatar-onboarding:${userId}:${resolvedAvatarId}`
}

export const isOnboardingReadyToFinish = (state: {
  hasAvatar: boolean
  hasPersona: boolean
  hasAgent: boolean
  hasTask: boolean
  pendingMemories: number
  confirmedMemories: number
}) => state.hasAvatar && state.hasPersona && state.hasAgent && state.hasTask && (state.pendingMemories > 0 || state.confirmedMemories > 0)
