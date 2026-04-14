<template>
  <div class="layout-shell">
    <!-- Mobile hamburger -->
    <button class="mobile-menu-btn" @click="drawerVisible = true">
      <span class="hamburger-icon">&#9776;</span>
    </button>

    <!-- Desktop sidebar -->
    <aside class="sidebar desktop-sidebar">
      <SidebarContent
        :auth="auth"
        :current-avatar-id="avatarStore.currentAvatarId"
        @logout="handleLogout"
      />
    </aside>

    <!-- Mobile drawer -->
    <el-drawer v-model="drawerVisible" direction="ltr" size="260px" :show-close="true" :title="t('app.title')">
      <SidebarContent
        :auth="auth"
        :current-avatar-id="avatarStore.currentAvatarId"
        @logout="handleLogout"
        @navigate="drawerVisible = false"
      />
    </el-drawer>

    <main class="content">
      <header class="topbar">
        <span class="topbar-title">{{ t('app.console') }}</span>
        <div class="topbar-right">
          <el-tag :type="providerStatus === 'ok' ? 'success' : 'warning'" size="small">
            {{ t('app.provider') }}: {{ providerStatus === 'ok' ? t('app.providerOnline') : t('app.providerMock') }}
          </el-tag>
          <el-dropdown @command="switchLocale" trigger="click">
            <el-button size="small" text>
              🌐 {{ localeStore.currentLocale === 'zh-CN' ? '中文' : 'EN' }}
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="zh-CN" :class="{ 'is-active': localeStore.currentLocale === 'zh-CN' }">中文</el-dropdown-item>
                <el-dropdown-item command="en-US" :class="{ 'is-active': localeStore.currentLocale === 'en-US' }">English</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <el-config-provider :locale="localeStore.elementLocale">
        <RouterView />
      </el-config-provider>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from './stores/auth'
import { useLocaleStore } from './stores/locale'
import { useAvatarStore } from './stores/avatar'
import api from './api/client'
import SidebarContent from './components/common/SidebarContent.vue'

const { t } = useI18n()
const auth = useAuthStore()
const localeStore = useLocaleStore()
const avatarStore = useAvatarStore()
const router = useRouter()
const providerStatus = ref<'ok' | 'degraded'>('degraded')
const drawerVisible = ref(false)

const switchLocale = (locale: string) => {
  localeStore.setLocale(locale as 'zh-CN' | 'en-US')
  const { locale: i18nLocale } = useI18n()
  i18nLocale.value = locale
}

onMounted(async () => {
  if (auth.accessToken) {
    try {
      const res = await api.get('/auth/me')
      auth.user = res.data
    } catch {
      // not logged in
    }
  }
  try {
    const res = await api.get('/provider/health')
    providerStatus.value = res.data?.status === 'ok' ? 'ok' : 'degraded'
  } catch {
    providerStatus.value = 'degraded'
  }
})

const handleLogout = async () => {
  await auth.logout()
  drawerVisible.value = false
  router.push('/login')
}
</script>

<style scoped>
.layout-shell {
  display: flex;
  min-height: 100vh;
}

/* Mobile hamburger - hidden on desktop */
.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 1000;
  background: #111827;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 1.2rem;
  cursor: pointer;
}

.hamburger-icon {
  line-height: 1;
}

/* Desktop sidebar */
.desktop-sidebar {
  background: #111827;
  color: white;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 220px;
  flex-shrink: 0;
}

.content {
  padding: 20px 24px;
  background: #f3f4f6;
  min-height: 100vh;
  flex: 1;
  min-width: 0;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.topbar-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .layout-shell {
    flex-direction: column;
  }

  .mobile-menu-btn {
    display: block;
  }

  .desktop-sidebar {
    display: none;
  }

  .content {
    padding: 60px 16px 20px;
  }
}
</style>
