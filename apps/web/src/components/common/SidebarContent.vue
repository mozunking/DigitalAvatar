<template>
  <div class="sidebar-inner">
    <div class="sidebar-logo">
      <h1>{{ t('app.title') }}</h1>
    </div>
    <nav>
      <RouterLink to="/dashboard" @click="$emit('navigate')">{{ t('nav.dashboard') }}</RouterLink>
      <RouterLink to="/avatars" @click="$emit('navigate')">{{ t('nav.avatars') }}</RouterLink>
      <RouterLink to="/avatars/new" @click="$emit('navigate')">{{ t('nav.newAvatar') }}</RouterLink>
      <RouterLink :to="currentAvatarId ? `/avatars/${currentAvatarId}/persona` : '/persona'" @click="$emit('navigate')">{{ t('nav.persona') }}</RouterLink>
      <RouterLink :to="currentAvatarId ? `/avatars/${currentAvatarId}/agents` : '/agents'" @click="$emit('navigate')">{{ t('nav.agents') }}</RouterLink>
      <RouterLink to="/tasks" @click="$emit('navigate')">{{ t('nav.tasks') }}</RouterLink>
      <RouterLink to="/memories/pending" @click="$emit('navigate')">{{ t('nav.memories') }}</RouterLink>
      <RouterLink to="/memories/search" @click="$emit('navigate')">{{ t('nav.memorySearch') }}</RouterLink>
      <RouterLink to="/audit" @click="$emit('navigate')">{{ t('nav.audit') }}</RouterLink>
      <RouterLink to="/settings" @click="$emit('navigate')">{{ t('nav.settings') }}</RouterLink>
    </nav>
    <div class="sidebar-footer">
      <div class="user-info">
        <span>{{ auth.user?.display_name || auth.user?.email }}</span>
      </div>
      <el-button size="small" text @click="$emit('logout')" class="logout-btn">{{ t('app.logout') }}</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { useAuthStore } from '../../stores/auth'

defineProps<{
  auth: ReturnType<typeof useAuthStore>
  currentAvatarId?: string
}>()

defineEmits<{
  logout: []
  navigate: []
}>()

const { t } = useI18n()
</script>

<style scoped>
.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-logo h1 {
  font-size: 1.1rem;
  margin: 0 0 8px;
  color: white;
}

nav {
  display: grid;
  gap: 2px;
  flex: 1;
}

nav a {
  color: #9ca3af;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: background 0.15s, color 0.15s;
}

nav a:hover {
  background: #1f2937;
  color: white;
}

nav a.router-link-active {
  background: #374151;
  color: white;
  font-weight: 600;
}

.sidebar-footer {
  border-top: 1px solid #374151;
  padding-top: 12px;
  margin-top: 12px;
}

.user-info {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  color: #9ca3af;
  font-size: 0.75rem;
  padding: 2px 0;
}
</style>
