import { defineStore } from 'pinia'
import type { UserResponse } from '../types/generated/api'
import { authApi } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('digital-avatar-access-token') || '',
    refreshToken: localStorage.getItem('digital-avatar-refresh-token') || '',
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
        this.accessToken = data.access_token
        this.refreshToken = data.refresh_token
        this.user = data.user
        localStorage.setItem('digital-avatar-access-token', data.access_token)
        localStorage.setItem('digital-avatar-refresh-token', data.refresh_token)
      } finally {
        this.loading = false
      }
    },
    async register(email: string, password: string, displayName?: string) {
      this.loading = true
      try {
        const { data } = await authApi.register(email, password, displayName)
        this.accessToken = data.access_token
        this.refreshToken = data.refresh_token
        this.user = data.user
        localStorage.setItem('digital-avatar-access-token', data.access_token)
        localStorage.setItem('digital-avatar-refresh-token', data.refresh_token)
      } finally {
        this.loading = false
      }
    },
    logout() {
      this.accessToken = ''
      this.refreshToken = ''
      this.user = null
      localStorage.removeItem('digital-avatar-access-token')
      localStorage.removeItem('digital-avatar-refresh-token')
    }
  }
})
