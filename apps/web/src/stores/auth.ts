import { defineStore } from 'pinia'
import type { UserResponse } from '../types/generated/api'
import { authApi } from '../api'
import { authTokenStorage } from '../api/authStorage'

const applySession = (
  store: {
    accessToken: string
    refreshToken: string
    user: UserResponse | null
  },
  payload: {
    accessToken: string
    refreshToken: string
    user: UserResponse | null
  }
) => {
  store.accessToken = payload.accessToken
  store.refreshToken = payload.refreshToken
  store.user = payload.user
  if (payload.accessToken && payload.refreshToken) {
    authTokenStorage.setTokens(payload.accessToken, payload.refreshToken)
    return
  }
  authTokenStorage.clear()
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: authTokenStorage.getAccessToken(),
    refreshToken: authTokenStorage.getRefreshToken(),
    user: null as UserResponse | null,
    loading: false
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken)
  },
  actions: {
    async login(email: string, password: string) {
      this.loading = true
      try {
        const { data } = await authApi.login(email, password)
        applySession(this, {
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          user: data.user
        })
      } finally {
        this.loading = false
      }
    },
    async register(email: string, password: string, displayName?: string) {
      this.loading = true
      try {
        const { data } = await authApi.register(email, password, displayName)
        applySession(this, {
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          user: data.user
        })
      } finally {
        this.loading = false
      }
    },
    clearSession() {
      applySession(this, {
        accessToken: '',
        refreshToken: '',
        user: null
      })
    },
    async logout() {
      const refreshToken = this.refreshToken || undefined
      try {
        await authApi.logout(refreshToken)
      } catch {
        // local cleanup must still happen even if server revocation already occurred
      } finally {
        this.clearSession()
      }
    }
  }
})
