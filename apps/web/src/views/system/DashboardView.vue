<template>
  <section class="page-card page-grid">
    <div class="header-row">
      <h2>{{ t('dashboard.title') }}</h2>
      <el-tag v-if="auth.user">{{ auth.user.email }}</el-tag>
    </div>

    <OnboardingGuide
      v-if="shouldShowOnboarding"
      :has-avatar="avatarStore.items.length > 0"
      :current-avatar-name="avatarStore.currentAvatar?.name"
      :has-persona="workspace.personas.length > 0"
      :has-agent="workspace.agents.length > 0"
      :has-task="workspace.tasks.length > 0"
      :pending-memories="workspace.memories.length"
      :confirmed-memories="workspace.confirmedMemories.length"
      :loading="workspace.loading || avatarStore.loading"
      :failed="Boolean(workspace.workspaceError)"
      :demo-loading="demoLoading"
      @create-demo="createDemoAvatar"
      @create-custom="$router.push('/avatars/new')"
      @open-persona="avatarStore.currentAvatarId && $router.push(`/avatars/${avatarStore.currentAvatarId}/persona`)"
      @open-agents="avatarStore.currentAvatarId && $router.push(`/avatars/${avatarStore.currentAvatarId}/agents`)"
      @open-tasks="$router.push('/tasks')"
      @open-memories="$router.push('/memories/pending')"
      @finish="finishOnboarding"
    />

    <template v-if="avatarStore.items.length > 0">
      <div class="avatar-selector">
        <el-select v-model="avatarStore.currentAvatarId" :placeholder="t('dashboard.selectAvatar')" @change="onAvatarChange">
          <el-option v-for="a in avatarStore.items" :key="a.id" :label="a.name" :value="a.id" />
        </el-select>
        <el-button @click="$router.push('/avatars/new')">{{ t('dashboard.createNew') }}</el-button>
      </div>

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
        :current-avatar-id="avatarStore.currentAvatarId"
        :personas="workspace.personas"
        :tasks="workspace.tasks"
        :pending-memories="workspace.memories"
        :confirmed-memories="workspace.confirmedMemories"
        :loading="workspace.loading"
        :failed="Boolean(workspace.workspaceError)"
      />

      <div class="quick-actions">
        <el-card v-if="!workspace.personas.length" shadow="hover" class="action-card" @click="avatarStore.currentAvatarId && $router.push(`/avatars/${avatarStore.currentAvatarId}/persona`)">
          <h3>{{ t('dashboard.generatePersona') }}</h3>
          <p>{{ t('dashboard.generatePersonaDesc') }}</p>
        </el-card>
        <el-card v-if="!workspace.agents.length" shadow="hover" class="action-card" @click="avatarStore.currentAvatarId && $router.push(`/avatars/${avatarStore.currentAvatarId}/agents`)">
          <h3>{{ t('dashboard.createAgent') }}</h3>
          <p>{{ t('dashboard.createAgentDesc') }}</p>
        </el-card>
        <el-card v-if="workspace.personas.length > 0 && workspace.agents.length > 0" shadow="hover" class="action-card" @click="$router.push('/tasks')">
          <h3>{{ t('dashboard.executeTask') }}</h3>
          <p>{{ t('dashboard.executeTaskDesc') }}</p>
        </el-card>
        <el-card v-if="workspace.memories.length > 0" shadow="hover" class="action-card action-warn" @click="$router.push('/memories/pending')">
          <h3>{{ workspace.memories.length }} {{ t('dashboard.pendingMemories') }}</h3>
          <p>{{ t('dashboard.viewMemories') }}</p>
        </el-card>
      </div>

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
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import GrowthReportCard from '../../components/common/GrowthReportCard.vue'
import OnboardingGuide from '../../components/common/OnboardingGuide.vue'
import { DEMO_AVATAR_GOAL, DEMO_AVATAR_NAME, getOnboardingStorageKey, isOnboardingReadyToFinish } from '../../components/common/onboarding'
import { useAvatarStore } from '../../stores/avatar'
import { useAuthStore } from '../../stores/auth'
import { useWorkspaceStore } from '../../stores/workspace'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()
const avatarStore = useAvatarStore()
const workspace = useWorkspaceStore()
const demoLoading = ref(false)
const onboardingDismissed = ref(false)

const progressStep = computed(() => {
  let step = 0
  if (avatarStore.items.length > 0) step++
  if (workspace.personas.length > 0) step++
  if (workspace.agents.length > 0) step++
  if (workspace.tasks.length > 0) step++
  return step
})

const onboardingStorageKey = computed(() => getOnboardingStorageKey(auth.user?.id || 'anonymous', avatarStore.currentAvatarId))

const shouldShowOnboarding = computed(() => {
  if (!auth.user) return false
  if (avatarStore.items.length === 0) return true
  return !onboardingDismissed.value
})

const syncOnboardingDismissed = () => {
  if (avatarStore.items.length === 0) {
    onboardingDismissed.value = false
    return
  }
  onboardingDismissed.value = localStorage.getItem(onboardingStorageKey.value) === 'done'
}

const onAvatarChange = async () => {
  await loadCurrentAvatarWorkspace()
}

const loadCurrentAvatarWorkspace = async () => {
  if (!avatarStore.currentAvatarId) return
  await workspace.loadAvatarWorkspace(avatarStore.currentAvatarId)
  await workspace.loadPendingMemories()
}

const load = async () => {
  await avatarStore.fetchAll()
  syncOnboardingDismissed()
  await loadCurrentAvatarWorkspace()
}

const createDemoAvatar = async () => {
  demoLoading.value = true
  try {
    const existingDemo = avatarStore.items.find((item) => item.name === DEMO_AVATAR_NAME)
    if (existingDemo) {
      avatarStore.setCurrentAvatar(existingDemo.id)
    } else {
      await avatarStore.create({
        name: DEMO_AVATAR_NAME,
        goal: DEMO_AVATAR_GOAL,
        visibility: 'private'
      })
    }
    syncOnboardingDismissed()
    ElMessage.success(t('dashboard.demoReady'))
    if (avatarStore.currentAvatarId) {
      await router.push(`/avatars/${avatarStore.currentAvatarId}/persona`)
    }
  } finally {
    demoLoading.value = false
  }
}

const finishOnboarding = () => {
  if (!isOnboardingReadyToFinish({
    hasAvatar: avatarStore.items.length > 0,
    hasPersona: workspace.personas.length > 0,
    hasAgent: workspace.agents.length > 0,
    hasTask: workspace.tasks.length > 0,
    pendingMemories: workspace.memories.length,
    confirmedMemories: workspace.confirmedMemories.length,
  })) {
    return
  }
  localStorage.setItem(onboardingStorageKey.value, 'done')
  onboardingDismissed.value = true
  ElMessage.success(t('dashboard.onboardingCompleted'))
}

watch(() => avatarStore.currentAvatarId, async (id, previousId) => {
  syncOnboardingDismissed()
  if (id && id !== previousId) {
    await loadCurrentAvatarWorkspace()
  }
})

watch(() => auth.user?.id, syncOnboardingDismissed)

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

