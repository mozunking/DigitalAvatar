<template>
  <section class="page-card page-grid">
    <h2>{{ t('memories.searchTitle') }}</h2>
    <div class="search-bar">
      <el-input v-model="query" :placeholder="t('memories.searchPlaceholder')" clearable @keyup.enter="doSearch" class="search-input">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="typeFilter" :placeholder="t('memories.typeFilter')" clearable class="type-select">
        <el-option label="Profile" value="profile" />
        <el-option label="Episodic" value="episodic" />
        <el-option label="Knowledge" value="knowledge" />
      </el-select>
      <el-button type="primary" @click="doSearch">{{ t('memories.search') }}</el-button>
    </div>

    <el-empty v-if="results.length === 0 && !loading" :description="t('memories.noResults')" />
    <div v-else class="list-grid">
      <article v-for="memory in results" :key="memory.id" class="list-item memory-card" @click="openDetail(memory)">
        <div class="memory-header">
          <el-tag size="small" :type="tagType(memory.type)">{{ memory.type }}</el-tag>
          <small>{{ formatDate(memory.created_at) }}</small>
        </div>
        <p class="memory-content">{{ memory.excerpt }}</p>
      </article>
    </div>
  </section>

  <!-- Memory Detail Drawer -->
  <el-drawer v-model="drawerVisible" :title="t('memories.detailTitle')" size="420px">
    <el-skeleton v-if="detailLoading" animated :rows="6" />
    <template v-else-if="selectedMemory">
      <el-descriptions :column="1" border>
        <el-descriptions-item :label="t('memories.type')">{{ selectedMemory.type }}</el-descriptions-item>
        <el-descriptions-item :label="t('memories.state')">
          <el-tag size="small">{{ selectedMemory.state }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('memories.sensitivity')">{{ selectedMemory.sensitivity }}</el-descriptions-item>
        <el-descriptions-item :label="t('memories.createdAt')">{{ formatDate(selectedMemory.created_at) }}</el-descriptions-item>
      </el-descriptions>
      <div class="detail-content">
        <h4>{{ t('memories.content') }}</h4>
        <p>{{ selectedMemory.content }}</p>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useAvatarStore } from '../../stores/avatar'
import { useWorkspaceStore } from '../../stores/workspace'
import type { MemoryResponse, MemorySummaryResponse } from '../../types/generated/api'

const { t } = useI18n()
const avatarStore = useAvatarStore()
const workspace = useWorkspaceStore()

const query = ref('')
const typeFilter = ref('')
const results = ref<MemorySummaryResponse[]>([])
const loading = ref(false)
const drawerVisible = ref(false)
const detailLoading = ref(false)
const selectedMemory = ref<MemoryResponse | null>(null)

const tagType = (type: string) => {
  const map: Record<string, string> = { profile: 'success', episodic: 'primary', knowledge: 'warning' }
  return map[type] || 'info'
}

const formatDate = (d: string) => new Date(d).toLocaleString()

const openDetail = async (memory: MemorySummaryResponse) => {
  if (!avatarStore.currentAvatarId) return
  drawerVisible.value = true
  detailLoading.value = true
  selectedMemory.value = null
  try {
    selectedMemory.value = await workspace.getMemoryDetail(avatarStore.currentAvatarId, memory.id)
  } catch {
    drawerVisible.value = false
    ElMessage.error(t('memories.searchFailed'))
  } finally {
    detailLoading.value = false
  }
}

const doSearch = async () => {
  if (!avatarStore.currentAvatarId) return
  loading.value = true
  try {
    results.value = await workspace.searchMemories(
      avatarStore.currentAvatarId,
      query.value || undefined,
      typeFilter.value || undefined,
    )
  } catch {
    ElMessage.error(t('memories.searchFailed'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (avatarStore.currentAvatarId) doSearch()
})
</script>

<style scoped>
.search-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.search-input { flex: 1; }
.type-select { width: 150px; }
.memory-card { cursor: pointer; transition: transform 0.15s; }
.memory-card:hover { transform: translateY(-2px); }
.memory-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.memory-content { font-size: 0.875rem; color: #374151; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }
.detail-content { margin-top: 16px; }
.detail-content h4 { margin: 0 0 8px; font-size: 0.875rem; color: #666; }
.detail-content p { font-size: 0.9rem; line-height: 1.6; color: #1f2937; }
</style>
