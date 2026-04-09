<template>
  <section class="page-card page-grid">
    <h2>{{ t('tasks.title') }}</h2>

    <div class="form-grid">
      <!-- Avatar selector -->
      <el-select v-model="selectedAvatarId" :placeholder="t('tasks.selectAvatar')" @change="onAvatarChange">
        <el-option v-for="a in avatarStore.items" :key="a.id" :label="a.name" :value="a.id" />
      </el-select>

      <!-- Agent selector -->
      <el-select v-model="agentId" :placeholder="t('tasks.selectAgent')" :disabled="!selectedAvatarId || agents.length === 0">
        <el-option v-for="agent in agents" :key="agent.id" :label="agent.name" :value="agent.id" />
      </el-select>

      <!-- Task input -->
      <el-input
        v-model="input"
        type="textarea"
        :rows="5"
        :placeholder="t('tasks.inputPlaceholder')"
      />

      <div class="task-actions">
        <el-button
          type="primary"
          @click="run"
          :disabled="!agentId || !selectedAvatarId || submitting"
          :loading="submitting"
        >
          {{ t('tasks.runTask') }}
        </el-button>
        <el-button @click="refreshTasks" :disabled="!selectedAvatarId">{{ t('tasks.refreshTasks') }}</el-button>
      </div>
    </div>

    <!-- Task list -->
    <el-skeleton :loading="tasksLoading" animated :count="3">
      <template #default>
        <el-empty v-if="tasks.length === 0 && !tasksLoading" :description="t('tasks.noTasks')" />

        <div class="list-grid">
          <article v-for="task in tasks" :key="task.task_id" class="list-item task-item" :class="`task-${task.status}`">
            <div class="task-header">
              <el-tag :type="statusType(task.status)" size="small">{{ task.status }}</el-tag>
              <small class="trace-id">trace_id: {{ task.trace_id }}</small>
            </div>
            <div class="task-body">
              <template v-if="task.status === 'succeeded' && task.result">
                <p class="task-result">{{ task.result }}</p>
              </template>
              <template v-else-if="task.status === 'failed' && task.error">
                <p class="task-error">{{ task.error }}</p>
              </template>
              <template v-else-if="task.status === 'blocked'">
                <p class="task-blocked">{{ task.error || t('tasks.blockedByPolicy') }}</p>
                <el-button size="small" type="warning" @click="retry(task)">{{ t('tasks.retry') }}</el-button>
              </template>
              <template v-else-if="task.status === 'running'">
                <p class="task-pending">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  {{ t('tasks.running') }}
                </p>
              </template>
              <template v-else>
                <p class="task-pending">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  {{ t('tasks.pendingResult') }}
                </p>
              </template>
            </div>
          </article>
        </div>
      </template>
    </el-skeleton>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useAvatarStore } from '../../stores/avatar'
import { useWorkspaceStore } from '../../stores/workspace'
import { taskApi } from '../../api'
import type { AgentResponse, TaskResponse } from '../../types/generated/api'

const { t } = useI18n()
const avatarStore = useAvatarStore()
const workspace = useWorkspaceStore()

const selectedAvatarId = ref(avatarStore.currentAvatarId || '')
const agentId = ref('')
const input = ref('Summarize today\'s priorities and note one safe follow-up task.')
const submitting = ref(false)
const tasksLoading = ref(false)
const agents = ref<AgentResponse[]>([])
const tasks = ref<TaskResponse[]>([])
const activePollers = new Map<string, boolean>()

const terminalStates = ['succeeded', 'failed', 'blocked']

const statusType = (status: string) => {
  const map: Record<string, string> = { succeeded: 'success', failed: 'danger', blocked: 'warning', running: '', pending: 'info' }
  return map[status] || 'info'
}

const loadWorkspace = async () => {
  if (!selectedAvatarId.value) return
  tasksLoading.value = true
  try {
    await workspace.loadAvatarWorkspace(selectedAvatarId.value)
    agents.value = workspace.agents
    if (!agentId.value && agents.value.length > 0) {
      agentId.value = agents.value[0].id
    }
    await refreshTasks()
  } finally {
    tasksLoading.value = false
  }
}

const refreshTasks = async () => {
  if (!selectedAvatarId.value) return
  try {
    const { data } = await taskApi.list(selectedAvatarId.value)
    tasks.value = data.items
    tasks.value
      .filter((task) => task.status === 'pending' || task.status === 'running')
      .forEach((task) => startPolling(task.task_id))
  } catch {
    // handled by global error handler
  }
}

const onAvatarChange = () => {
  stopAllPolling()
  agentId.value = ''
  agents.value = []
  tasks.value = []
  loadWorkspace()
}

const run = async () => {
  if (!selectedAvatarId.value || !agentId.value) return
  submitting.value = true
  try {
    const { data: task } = await taskApi.create({
      avatar_id: selectedAvatarId.value,
      agent_id: agentId.value,
      input: input.value,
    })
    tasks.value.unshift(task)
    ElMessage.success(`${t('tasks.executed')} · trace_id: ${task.trace_id}`)

    if (task.status === 'pending' || task.status === 'running') {
      startPolling(task.task_id)
    }
  } finally {
    submitting.value = false
  }
}

const showTerminalMessage = (task: TaskResponse) => {
  if (task.status === 'succeeded') {
    ElMessage.success(t('tasks.succeededWithTrace', { traceId: task.trace_id }))
    workspace.loadPendingMemories()
    workspace.loadAuditLogs({ trace_id: task.trace_id })
    return
  }
  if (task.status === 'blocked') {
    ElMessage.warning(t('tasks.blockedWithTrace', { traceId: task.trace_id }))
    workspace.loadAuditLogs({ trace_id: task.trace_id })
    return
  }
  if (task.status === 'failed') {
    ElMessage.error(task.error || t('tasks.failedWithTrace', { traceId: task.trace_id }))
    workspace.loadAuditLogs({ trace_id: task.trace_id })
  }
}

const stopPolling = (taskId: string) => {
  activePollers.delete(taskId)
}

const stopAllPolling = () => {
  activePollers.clear()
}

const startPolling = (taskId: string) => {
  if (activePollers.has(taskId)) return
  activePollers.set(taskId, true)
  void pollTaskStatus(taskId)
}

const pollTaskStatus = async (taskId: string, maxAttempts = 15, interval = 2000) => {
  for (let i = 0; i < maxAttempts; i++) {
    if (!activePollers.has(taskId)) {
      return
    }

    await new Promise(resolve => setTimeout(resolve, interval))

    try {
      const { data: updated } = await taskApi.get(taskId)
      const idx = tasks.value.findIndex(t => t.task_id === taskId)
      const previous = idx >= 0 ? tasks.value[idx] : undefined
      if (idx >= 0) {
        tasks.value[idx] = updated
      }
      if (terminalStates.includes(updated.status)) {
        stopPolling(taskId)
        if (!previous || previous.status !== updated.status) {
          showTerminalMessage(updated)
        }
        return
      }
    } catch {
      stopPolling(taskId)
      return
    }
  }

  const task = tasks.value.find(item => item.task_id === taskId)
  if (task) {
    ElMessage.info(t('tasks.pendingTimeout', { traceId: task.trace_id }))
  }
  stopPolling(taskId)
}

const retry = (_task: TaskResponse) => {
  input.value = ''
  ElMessage.info(t('tasks.modifyAndRetry'))
}

watch(() => avatarStore.currentAvatarId, (id) => {
  if (id && !selectedAvatarId.value) {
    selectedAvatarId.value = id
  }
})

onMounted(async () => {
  await avatarStore.fetchAll()
  if (selectedAvatarId.value) {
    loadWorkspace()
  }
})

onBeforeUnmount(() => {
  stopAllPolling()
})
</script>

<style scoped>
.form-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.task-actions {
  display: flex;
  gap: 8px;
}

.task-item {
  border-left: 3px solid transparent;
  padding: 12px;
}

.task-item.task-succeeded { border-left-color: #67c23a; }
.task-item.task-failed { border-left-color: #f56c6c; }
.task-item.task-blocked { border-left-color: #e6a23c; }
.task-item.task-pending, .task-item.task-running { border-left-color: #909399; }

.task-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.trace-id {
  color: #9ca3af;
  font-size: 0.75rem;
}

.task-result {
  font-size: 0.875rem;
  color: #374151;
  white-space: pre-wrap;
}

.task-error, .task-blocked {
  font-size: 0.875rem;
  color: #f56c6c;
}

.task-pending {
  font-size: 0.875rem;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
