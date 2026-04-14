export const AUTH_STORAGE_KEYS = {
  accessToken: 'digital-avatar-access-token',
  refreshToken: 'digital-avatar-refresh-token',
} as const

export const authTokenStorage = {
  getAccessToken: () => localStorage.getItem(AUTH_STORAGE_KEYS.accessToken) || '',
  getRefreshToken: () => localStorage.getItem(AUTH_STORAGE_KEYS.refreshToken) || '',
  setTokens(accessToken: string, refreshToken: string) {
    localStorage.setItem(AUTH_STORAGE_KEYS.accessToken, accessToken)
    localStorage.setItem(AUTH_STORAGE_KEYS.refreshToken, refreshToken)
  },
  clear() {
    localStorage.removeItem(AUTH_STORAGE_KEYS.accessToken)
    localStorage.removeItem(AUTH_STORAGE_KEYS.refreshToken)
  }
}
