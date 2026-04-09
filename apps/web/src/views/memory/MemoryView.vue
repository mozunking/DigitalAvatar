<template>
  <section class="page-card page-grid">
    <h2>{{ t('memories.title') }}</h2>

    <div class="toolbar">
      <el-button type="primary" @click="refresh">{{ t('memories.refresh') }}</el-button>
      <el-tag v-if="workspace.memories.length > 0" type="warning">{{ workspace.memories.length }} {{ t('memories.pendingCount') }}</el-tag>
    </div>

    <el-skeleton :loading="loading" animated :count="3">
      <template #default>
        <el-empty v-if="workspace.memories.length === 0 && !loading" :description="t('memories.noPending')" />

        <div class="memory-cards">
          <el-card v-for="memory in workspace.memories" :key="memory.id" shadow="hover" class="memory-card">
            <!-- Header -->
            <div class="memory-header">
              <el-tag size="small">{{ memory.type }}</el-tag>
              <el-tag v-if="memory.sensitivity === 'high'" type="danger" size="small" effect="dark">
                {{ t('memories.highRisk') }}
              </el-tag>
              <el-tag v-else-if="memory.sensitivity === 'medium'" type="warning" size="small">
                {{ t('memories.mediumRisk') }}
              </el-tag>
              <el-tag :type="memory.state === 'pending_confirm' ? 'warning' : 'info'" size="small">{{ memory.state }}</el-tag>
            </div>

            <!-- Content -->
            <div class="memory-content">
              <p>{{ memory.content }}</p>
            </div>

            <!-- Source info -->
            <div class="memory-source" v-if="memory.source_type || memory.task_id">
              <el-divider />
              <small>
                <strong>{{ t('memories.source') }}:</strong>
                {{ memory.source_type || '-' }}
                <template v-if="memory.task_id">
                  &nbsp;|&nbsp;
                  <strong>{{ t('memories.fromTask') }}:</strong>
                  <router-link :to="`/tasks`">{{ memory.task_id.slice(0, 8) }}...</router-link>
                </template>
              </small>
            </div>

            <!-- Created -->
            <div class="memory-meta">
              <small>{{ formatDate(memory.created_at) }}</small>
            </div>

            <!-- Reason input -->
            <div class="reason-section">
              <el-input
                v-model="reasons[memory.id]"
                :placeholder="t('memories.reasonPlaceholder')"
                size="small"
                clearable
              />
            </div>

            <!-- Actions -->
            <div class="memory-actions">
              <el-button type="success" size="small" @click="confirm(memory.id)" :loading="acting[memory.id] === 'confirm'">
                {{ t('memories.confirm') }}
              </el-button>
              <el-button type="danger" size="small" @click="reject(memory.id)" :loading="acting[memory.id] === 'reject'">
                {{ t('memories.reject') }}
              </el-button>
            </div>
          </el-card>
        </div>
      </template>
    </el-skeleton>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useWorkspaceStore } from '../../stores/workspace'

const { t } = useI18n()
const workspace = useWorkspaceStore()
const loading = ref(false)
const reasons = reactive<Record<string, string>>({})
const acting = reactive<Record<string, string>>({})

const formatDate = (d: string) => new Date(d).toLocaleString()

const refresh = async () => {
  loading.value = true
  try {
    await workspace.loadPendingMemories()
  } finally {
    loading.value = false
  }
}

const confirm = async (memoryId: string) => {
  acting[memoryId] = 'confirm'
  try {
    await workspace.confirmMemory(memoryId, reasons[memoryId])
    delete reasons[memoryId]
    ElMessage.success(t('memories.confirmed'))
  } finally {
    delete acting[memoryId]
  }
}

const reject = async (memoryId: string) => {
  acting[memoryId] = 'reject'
  try {
    await workspace.rejectMemory(memoryId, reasons[memoryId])
    delete reasons[memoryId]
    ElMessage.success(t('memories.rejected'))
  } finally {
    delete acting[memoryId]
  }
}

onMounted(refresh)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.memory-cards {
  display: grid;
  gap: 12px;
}

.memory-card {
  transition: transform 0.15s;
}

.memory-card:hover {
  transform: translateY(-1px);
}

.memory-header {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 8px;
}

.memory-content {
  padding: 8px 0;
  font-size: 0.9rem;
  color: #374151;
  line-height: 1.5;
}

.memory-source {
  color: #6b7280;
  font-size: 0.8rem;
}

.memory-source a {
  color: #409eff;
  text-decoration: none;
}

.memory-meta {
  margin-top: 4px;
  color: #9ca3af;
  font-size: 0.75rem;
}

.reason-section {
  margin-top: 8px;
}

.memory-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
</style>
