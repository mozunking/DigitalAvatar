import { defineStore } from 'pinia'
import { avatarApi } from '../api'
import type { AvatarResponse } from '../types/generated/api'

export const useAvatarStore = defineStore('avatars', {
  state: () => ({
    items: [] as AvatarResponse[],
    loading: false,
    currentAvatarId: ''
  }),
  getters: {
    currentAvatar: (state) => state.items.find((item) => item.id === state.currentAvatarId) || null
  },
  actions: {
    async fetchAll() {
      this.loading = true
      try {
        const { data } = await avatarApi.list()
        this.items = data.items
        if (!this.currentAvatarId && this.items.length > 0) {
          this.currentAvatarId = this.items[0].id
        }
      } finally {
        this.loading = false
      }
    },
    async create(payload: { name: string; goal: string; visibility: string }) {
      const { data } = await avatarApi.create(payload)
      this.items.unshift(data)
      this.currentAvatarId = data.id
      return data
    },
    async update(payload: { id: string; name: string; goal: string; visibility: string }) {
      const { data } = await avatarApi.update(payload.id, payload)
      const index = this.items.findIndex((item) => item.id === payload.id)
      if (index >= 0) {
        this.items[index] = data
      }
      return data
    },
    setCurrentAvatar(id: string) {
      this.currentAvatarId = id
    }
  }
})
