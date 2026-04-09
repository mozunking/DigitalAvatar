<template>
  <section class="page-card page-grid">
    <div class="header-row">
      <h2>{{ t('dashboard.title') }}</h2>
      <el-tag v-if="auth.user">{{ auth.user.email }}</el-tag>
    </div>

    <!-- 无 Avatar 状态 -->
    <el-empty v-if="avatarStore.items.length === 0 && !avatarStore.loading" :description="t('dashboard.noAvatar')">
      <el-button type="primary" @click="$router.push('/avatars/new')">{{ t('dashboard.createFirst') }}</el-button>
    </el-empty>

    <template v-else>
      <!-- Avatar 选择 -->
      <div class="avatar-selector">
        <el-select v-model="avatarStore.currentAvatarId" :placeholder="t('dashboard.selectAvatar')" @change="onAvatarChange">
          <el-option v-for="a in avatarStore.items" :key="a.id" :label="a.name" :value="a.id" />
        </el-select>
        <el-button @click="$router.push('/avatars/new')">{{ t('dashboard.createNew') }}</el-button>
      </div>

      <!-- 进度指引 -->
      <el-steps :active="progressStep" align-center class="progress-steps">
        <el-step title="Avatar" :description="avatarStore.items.length > 0 ? avatarStore.currentAvatar?.name : t('dashboard.notCreated')" />
        <el-step title="Persona" :description="workspace.personas.length > 0 ? `v${workspace.personas[0].version}` : t('dashboard.pendingGenerate')" />
        <el-step title="Agent" :description="workspace.agents.length > 0 ? `${workspace.agents.length} ${t('dashboard.toCreate')}` : t('dashboard.pendingCreate')" />
        <el-step title="Task" :description="workspace.tasks.length > 0 ? t('dashboard.executed') : t('dashboard.pending')" />
        <el-step title="Memory" :description="workspace.memories.length > 0 ? `${workspace.memories.length} ${t('dashboard.pendingConfirm')}` : t('dashboard.none')" />
      </el-steps>

      <GrowthReportCard
        v-if="avatarStore.currentAvatar"
        :avatar-name="avatarStore.currentAvatar.name"
        :personas="workspace.personas"
        :tasks="workspace.tasks"
        :pending-memories="workspace.memories"
        :confirmed-memories="workspace.confirmedMemories"
      />

      <!-- 快速操作 -->
      <div class="quick-actions">
        <el-card v-if="!workspace.personas.length" shadow="hover" class="action-card" @click="$router.push('/persona')">
          <h3>{{ t('dashboard.generatePersona') }}</h3>
          <p>{{ t('dashboard.generatePersonaDesc') }}</p>
        </el-card>
        <el-card v-if="!workspace.agents.length" shadow="hover" class="action-card" @click="$router.push('/agents')">
          <h3>{{ t('dashboard.createAgent') }}</h3>
          <p>{{ t('dashboard.createAgentDesc') }}</p>
        </el-card>
        <el-card v-if="workspace.personas.length > 0 && workspace.agents.length > 0" shadow="hover" class="action-card" @click="$router.push('/tasks')">
          <h3>{{ t('dashboard.executeTask') }}</h3>
          <p>{{ t('dashboard.executeTaskDesc') }}</p>
        </el-card>
        <el-card v-if="workspace.memories.length > 0" shadow="hover" class="action-card action-warn" @click="$router.push('/memories')">
          <h3>{{ workspace.memories.length }} {{ t('dashboard.pendingMemories') }}</h3>
          <p>{{ t('dashboard.viewMemories') }}</p>
        </el-card>
      </div>

      <!-- 最近任务 -->
      <div v-if="workspace.tasks.length > 0">
        <h3>{{ t('dashboard.recentTasks') }}</h3>
        <div class="list-grid">
          <article v-for="task in workspace.tasks.slice(0, 5)" :key="task.task_id" class="list-item">
            <div class="task-row">
              <el-tag :type="task.status === 'succeeded' ? 'success' : task.status === 'failed' ? 'danger' : 'info'" size="small">{{ task.status }}</el-tag>
              <span class="task-input">{{ task.result || task.error || task.status }}</span>
            </div>
            <small>trace_id: {{ task.trace_id }}</small>
          </article>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import GrowthReportCard from '../../components/common/GrowthReportCard.vue'
import { useAvatarStore } from '../../stores/avatar'
import { useAuthStore } from '../../stores/auth'
import { useWorkspaceStore } from '../../stores/workspace'

const { t } = useI18n()
const auth = useAuthStore()
const avatarStore = useAvatarStore()
const workspace = useWorkspaceStore()

const progressStep = computed(() => {
  let step = 0
  if (avatarStore.items.length > 0) step++
  if (workspace.personas.length > 0) step++
  if (workspace.agents.length > 0) step++
  if (workspace.tasks.length > 0) step++
  return step
})

const onAvatarChange = () => {
  workspace.loadAvatarWorkspace(avatarStore.currentAvatarId)
  workspace.loadPendingMemories()
}

const load = async () => {
  await avatarStore.fetchAll()
  if (avatarStore.currentAvatarId) {
    await workspace.loadAvatarWorkspace(avatarStore.currentAvatarId)
    await workspace.loadPendingMemories()
  }
}

watch(() => avatarStore.currentAvatarId, (id) => {
  if (id) {
    workspace.loadAvatarWorkspace(id)
    workspace.loadPendingMemories()
  }
})

onMounted(load)
</script>

<style scoped>
.header-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-selector {
  display: flex;
  gap: 8px;
  align-items: center;
}

.progress-steps {
  margin: 16px 0;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.action-card {
  cursor: pointer;
  transition: transform 0.15s;
}

.action-card:hover {
  transform: translateY(-2px);
}

.action-card h3 {
  margin: 0 0 4px;
  font-size: 1rem;
}

.action-card p {
  margin: 0;
  color: #666;
  font-size: 0.875rem;
}

.action-warn {
  border-color: #f56c6c;
}

.task-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 4px;
}

.task-input {
  font-size: 0.875rem;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 400px;
}
</style>

