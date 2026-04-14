<template>
  <el-card shadow="never" class="onboarding-guide">
    <template #header>
      <div class="guide-header">
        <div>
          <div class="guide-eyebrow">{{ t('dashboard.onboardingEyebrow') }}</div>
          <h3>{{ t('dashboard.onboardingTitle') }}</h3>
          <p>{{ t('dashboard.onboardingDescription') }}</p>
        </div>
        <el-tag :type="statusTagType">{{ statusLabel }}</el-tag>
      </div>
    </template>

    <el-alert
      v-if="failed"
      :title="t('dashboard.onboardingFailedTitle')"
      :description="t('dashboard.onboardingFailedDescription')"
      type="warning"
      :closable="false"
      show-icon
      class="guide-alert"
    />

    <div class="guide-actions">
      <el-button type="primary" :loading="demoLoading" @click="$emit('create-demo')">
        {{ t('dashboard.useDemoAvatar') }}
      </el-button>
      <el-button @click="$emit('create-custom')">{{ t('dashboard.createCustomAvatar') }}</el-button>
    </div>

    <div class="guide-steps">
      <article v-for="step in steps" :key="step.key" class="guide-step" :class="{ done: step.done }">
        <div class="step-main">
          <div class="step-title-row">
            <h4>{{ step.title }}</h4>
            <el-tag size="small" :type="step.done ? 'success' : 'info'">
              {{ step.done ? t('dashboard.onboardingDone') : t('dashboard.onboardingTodo') }}
            </el-tag>
          </div>
          <p>{{ step.description }}</p>
          <small v-if="step.detail">{{ step.detail }}</small>
        </div>
        <el-button v-if="step.actionLabel" text type="primary" @click="triggerStepAction(step.actionEvent)">
          {{ step.actionLabel }}
        </el-button>
      </article>
    </div>

    <el-alert
      :title="t('dashboard.onboardingHintTitle')"
      :description="hintText"
      type="info"
      :closable="false"
      show-icon
      class="guide-alert"
    />

    <div class="guide-footer">
      <el-button :disabled="!readyToFinish || loading" @click="$emit('finish')">
        {{ t('dashboard.finishOnboarding') }}
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { isOnboardingReadyToFinish } from './onboarding'

const props = defineProps<{
  hasAvatar: boolean
  currentAvatarName?: string
  hasPersona: boolean
  hasAgent: boolean
  hasTask: boolean
  pendingMemories: number
  confirmedMemories: number
  loading?: boolean
  failed?: boolean
  demoLoading?: boolean
}>()

const emit = defineEmits<{
  (event: 'create-demo'): void
  (event: 'create-custom'): void
  (event: 'open-persona'): void
  (event: 'open-agents'): void
  (event: 'open-tasks'): void
  (event: 'open-memories'): void
  (event: 'finish'): void
}>()

type StepActionEvent = 'create-demo' | 'open-persona' | 'open-agents' | 'open-tasks' | 'open-memories'

const { t } = useI18n()

const readyToFinish = computed(() => isOnboardingReadyToFinish({
  hasAvatar: props.hasAvatar,
  hasPersona: props.hasPersona,
  hasAgent: props.hasAgent,
  hasTask: props.hasTask,
  pendingMemories: props.pendingMemories,
  confirmedMemories: props.confirmedMemories,
}))

const completedSteps = computed(() => {
  let count = 0
  if (props.hasAvatar) count++
  if (props.hasPersona) count++
  if (props.hasAgent) count++
  if (props.hasTask) count++
  if (props.pendingMemories > 0 || props.confirmedMemories > 0) count++
  return count
})

const statusLabel = computed(() => readyToFinish.value
  ? t('dashboard.onboardingReadyState')
  : t('dashboard.onboardingProgressState', { done: completedSteps.value, total: 5 }))

const statusTagType = computed(() => readyToFinish.value ? 'success' : 'info')

const steps = computed(() => [
  {
    key: 'avatar',
    title: t('dashboard.stepAvatarTitle'),
    description: props.hasAvatar ? t('dashboard.stepAvatarDone') : t('dashboard.stepAvatarPending'),
    detail: props.currentAvatarName || '',
    done: props.hasAvatar,
    actionLabel: !props.hasAvatar ? t('dashboard.useDemoAvatar') : '',
    actionEvent: 'create-demo' as StepActionEvent,
  },
  {
    key: 'persona',
    title: t('dashboard.stepPersonaTitle'),
    description: props.hasPersona ? t('dashboard.stepPersonaDone') : t('dashboard.stepPersonaPending'),
    detail: '',
    done: props.hasPersona,
    actionLabel: t('dashboard.openPersona'),
    actionEvent: 'open-persona' as StepActionEvent,
  },
  {
    key: 'agent',
    title: t('dashboard.stepAgentTitle'),
    description: props.hasAgent ? t('dashboard.stepAgentDone') : t('dashboard.stepAgentPending'),
    detail: '',
    done: props.hasAgent,
    actionLabel: t('dashboard.openAgents'),
    actionEvent: 'open-agents' as StepActionEvent,
  },
  {
    key: 'task',
    title: t('dashboard.stepTaskTitle'),
    description: props.hasTask ? t('dashboard.stepTaskDone') : t('dashboard.stepTaskPending'),
    detail: '',
    done: props.hasTask,
    actionLabel: t('dashboard.openTasks'),
    actionEvent: 'open-tasks' as StepActionEvent,
  },
  {
    key: 'memory',
    title: t('dashboard.stepMemoryTitle'),
    description: props.pendingMemories > 0 || props.confirmedMemories > 0
      ? t('dashboard.stepMemoryDone', { pending: props.pendingMemories, confirmed: props.confirmedMemories })
      : t('dashboard.stepMemoryPending'),
    detail: '',
    done: props.pendingMemories > 0 || props.confirmedMemories > 0,
    actionLabel: t('dashboard.openMemories'),
    actionEvent: 'open-memories' as StepActionEvent,
  },
])

const triggerStepAction = (event: StepActionEvent) => {
  if (event === 'create-demo') emit('create-demo')
  if (event === 'open-persona') emit('open-persona')
  if (event === 'open-agents') emit('open-agents')
  if (event === 'open-tasks') emit('open-tasks')
  if (event === 'open-memories') emit('open-memories')
}

const hintText = computed(() => {
  if (!props.hasAvatar) return t('dashboard.onboardingHintAvatar')
  if (!props.hasPersona) return t('dashboard.onboardingHintPersona')
  if (!props.hasAgent) return t('dashboard.onboardingHintAgent')
  if (!props.hasTask) return t('dashboard.onboardingHintTask')
  if (props.pendingMemories === 0 && props.confirmedMemories === 0) return t('dashboard.onboardingHintMemory')
  return t('dashboard.onboardingHintFinish')
})
</script>

<style scoped>
.onboarding-guide {
  border: 1px solid #dbeafe;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}

.guide-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.guide-eyebrow {
  font-size: 12px;
  color: #2563eb;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.guide-header h3 {
  margin: 4px 0;
}

.guide-header p {
  margin: 0;
  color: #4b5563;
  max-width: 720px;
}

.guide-actions,
.guide-footer {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.guide-steps {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.guide-step {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fff;
}

.guide-step.done {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.step-main {
  display: grid;
  gap: 6px;
}

.step-title-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.step-title-row h4,
.step-main p,
.step-main small {
  margin: 0;
}

.step-main p {
  color: #374151;
}

.step-main small {
  color: #6b7280;
}

.guide-alert {
  margin-top: 16px;
}
</style>
