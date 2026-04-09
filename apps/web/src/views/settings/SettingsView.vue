<template>
  <section class="page-card page-grid">
    <h2>{{ t('settings.title') }}</h2>

    <!-- Provider 状态 -->
    <el-card shadow="never">
      <template #header>
        <span>{{ t('settings.providerStatus') }}</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item :label="t('settings.providerLabel')">
          <el-tag :type="providerInfo.mode === 'live' ? 'success' : 'warning'" size="small">
            {{ providerInfo.mode === 'live' ? t('settings.ollamaOnline') : t('settings.ollamaMock') }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('settings.model')">{{ providerInfo.model || t('settings.modelNotDetected') }}</el-descriptions-item>
        <el-descriptions-item :label="t('settings.ollamaUrl')">{{ providerInfo.url }}</el-descriptions-item>
      </el-descriptions>
      <div style="margin-top: 12px; color: #666; font-size: 0.875rem;">
        <p v-if="providerInfo.mode !== 'live'">
          {{ t('settings.ollamaNotConnected') }}<code>ollama serve</code>{{ t('settings.thenPull') }}<code>ollama pull qwen3.5:7b-instruct-q4_0</code>
        </p>
      </div>
    </el-card>

    <!-- 账户信息 -->
    <el-card shadow="never">
      <template #header>
        <span>{{ t('settings.accountInfo') }}</span>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item :label="t('settings.email')">{{ auth.user?.email }}</el-descriptions-item>
        <el-descriptions-item :label="t('settings.displayName')">{{ auth.user?.display_name || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 语言设置 -->
    <el-card shadow="never">
      <template #header>
        <span>{{ t('settings.language') }}</span>
      </template>
      <el-radio-group :model-value="localeStore.currentLocale" @change="switchLocale">
        <el-radio-button value="zh-CN">中文</el-radio-button>
        <el-radio-button value="en-US">English</el-radio-button>
      </el-radio-group>
    </el-card>

    <!-- 隐私操作 -->
    <el-card shadow="never">
      <template #header>
        <span>{{ t('settings.privacyActions') }}</span>
      </template>
      <div class="privacy-actions">
        <div class="privacy-item">
          <div>
            <strong>{{ t('settings.exportData') }}</strong>
            <p class="privacy-desc">{{ t('settings.exportDataDesc') }}</p>
          </div>
          <el-button @click="handleExport" :loading="exporting">{{ t('settings.export') }}</el-button>
        </div>
        <el-divider />
        <div class="privacy-item danger-zone">
          <div>
            <strong>{{ t('settings.deleteAccount') }}</strong>
            <p class="privacy-desc">{{ t('settings.deleteAccountDesc') }}</p>
          </div>
          <el-button type="danger" @click="deleteDialogVisible = true">{{ t('settings.delete') }}</el-button>
        </div>
      </div>
    </el-card>
  </section>

  <!-- 删除确认对话框 -->
  <el-dialog v-model="deleteDialogVisible" :title="t('settings.confirmDeleteTitle')" width="420px">
    <p>{{ t('settings.confirmDeleteMsg') }}</p>
    <p style="color: #f56c6c; font-weight: 600; margin-top: 8px;">{{ t('settings.irreversible') }}</p>
    <template #footer>
      <el-button @click="deleteDialogVisible = false">{{ t('settings.cancel') }}</el-button>
      <el-button type="danger" :loading="deleting" @click="handleDelete">{{ t('settings.confirmDelete') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'
import { useLocaleStore } from '../../stores/locale'
import api from '../../api/client'

const { t, locale } = useI18n()
const auth = useAuthStore()
const localeStore = useLocaleStore()
const router = useRouter()

const providerInfo = ref({ mode: 'unknown', model: '', url: 'http://localhost:11434' })
const exporting = ref(false)
const deleting = ref(false)
const deleteDialogVisible = ref(false)

const switchLocale = (val: string) => {
  localeStore.setLocale(val as 'zh-CN' | 'en-US')
  locale.value = val
}

onMounted(async () => {
  try {
    const res = await api.get('/provider/health')
    providerInfo.value = {
      mode: res.data?.mode || 'mock',
      model: res.data?.model || '',
      url: 'http://localhost:11434'
    }
  } catch {
    providerInfo.value.mode = 'mock'
  }
})

const handleExport = async () => {
  exporting.value = true
  try {
    const res = await api.get('/privacy/export')
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `digital-avatar-export-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(t('settings.exportSuccess'))
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.error?.message || t('settings.exportFailed'))
  } finally {
    exporting.value = false
  }
}

const handleDelete = async () => {
  deleting.value = true
  try {
    await api.delete('/privacy/delete')
    auth.logout()
    ElMessage.success(t('settings.accountDeleted'))
    router.push('/login')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.error?.message || t('settings.deleteFailed'))
  } finally {
    deleting.value = false
    deleteDialogVisible.value = false
  }
}
</script>

<style scoped>
.privacy-actions {
  display: flex;
  flex-direction: column;
}

.privacy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.danger-zone p {
  color: #666;
  margin: 4px 0 0;
  font-size: 0.875rem;
}

.privacy-desc {
  color: #666;
  margin: 4px 0 0;
  font-size: 0.875rem;
}

code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.875rem;
}
</style>
