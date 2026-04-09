<template>
  <el-card shadow="never" class="growth-report-card">
    <template #header>
      <div class="report-header">
        <div>
          <div class="eyebrow">{{ t('growthReport.eyebrow') }}</div>
          <h3>{{ t('growthReport.title') }}</h3>
        </div>
        <el-tag :type="statusTagType">{{ statusLabel }}</el-tag>
      </div>
    </template>

    <template v-if="reportState === 'empty'">
      <el-empty :description="t('growthReport.emptyDescription')">
        <el-button type="primary" @click="$router.push('/tasks')">{{ t('growthReport.runFirstTask') }}</el-button>
      </el-empty>
    </template>

    <template v-else-if="reportState === 'failed'">
      <el-alert
        :title="t('growthReport.failedTitle')"
        :description="t('growthReport.failedDescription')"
        type="error"
        :closable="false"
        show-icon
      />
    </template>

    <template v-else>
      <div class="snapshot-grid">
        <div class="snapshot-item">
          <div class="snapshot-label">{{ t('growthReport.confirmedMemories') }}</div>
          <div class="snapshot-value">{{ confirmedMemories.length }}</div>
        </div>
        <div class="snapshot-item">
          <div class="snapshot-label">{{ t('growthReport.pendingMemories') }}</div>
          <div class="snapshot-value">{{ pendingMemories.length }}</div>
        </div>
        <div class="snapshot-item">
          <div class="snapshot-label">{{ t('growthReport.personaVersion') }}</div>
          <div class="snapshot-value">{{ currentPersona ? `v${currentPersona.version}` : '—' }}</div>
        </div>
        <div class="snapshot-item">
          <div class="snapshot-label">{{ t('growthReport.lastUpdated') }}</div>
          <div class="snapshot-value snapshot-date">{{ latestGrowthAt ? formatDate(latestGrowthAt) : '—' }}</div>
        </div>
      </div>

      <div class="report-section">
        <div class="section-title-row">
          <h4>{{ t('growthReport.learnedTitle') }}</h4>
          <el-tag v-if="reportState === 'demo'" size="small" type="warning">{{ t('growthReport.demoTag') }}</el-tag>
        </div>
        <div v-if="learnedInsights.length > 0" class="insight-list">
          <article v-for="insight in learnedInsights" :key="insight.id" class="insight-item">
            <div class="insight-content">{{ insight.content }}</div>
            <div class="insight-meta">
              <span>{{ t('growthReport.evidence') }} {{ insight.evidence }}</span>
              <span>{{ formatDate(insight.created_at) }}</span>
            </div>
          </article>
        </div>
        <el-alert
          v-else
          :title="t('growthReport.buildingTitle')"
          :description="t('growthReport.buildingDescription')"
          type="info"
          :closable="false"
          show-icon
        />
      </div>

      <div class="report-section report-grid">
        <el-card shadow="never" class="report-subcard">
          <template #header>
            <h4>{{ t('growthReport.improvingTitle') }}</h4>
          </template>
          <ul class="bullet-list">
            <li v-for="item in improvementItems" :key="item">{{ item }}</li>
          </ul>
        </el-card>

        <el-card shadow="never" class="report-subcard">
          <template #header>
            <h4>{{ t('growthReport.nextActionsTitle') }}</h4>
          </template>
          <ul class="bullet-list action-list">
            <li v-for="item in nextActions" :key="item.label">
              <span>{{ item.label }}</span>
              <el-button text type="primary" @click="$router.push(item.to)">{{ t('growthReport.open') }}</el-button>
            </li>
          </ul>
        </el-card>
      </div>

      <el-alert
        :title="t('growthReport.traceabilityTitle')"
        :description="traceabilityDescription"
        type="success"
        :closable="false"
        show-icon
      />
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MemoryResponse, PersonaResponse, TaskResponse } from '../../types/generated/api'

const props = defineProps<{
  avatarName?: string
  personas: PersonaResponse[]
  tasks: TaskResponse[]
  pendingMemories: MemoryResponse[]
  confirmedMemories: MemoryResponse[]
  loading?: boolean
  failed?: boolean
}>()

const { t } = useI18n()

const currentPersona = computed(() => props.personas.find((item) => item.is_current) || props.personas[0] || null)

const reportState = computed<'empty' | 'building' | 'ready' | 'demo' | 'failed'>(() => {
  if (props.failed) return 'failed'
  const normalizedName = (props.avatarName || '').trim().toLowerCase()
  if (normalizedName === 'demo avatar') return 'demo'
  if (props.confirmedMemories.length > 0) return 'ready'
  if (props.tasks.length > 0 || props.pendingMemories.length > 0 || props.personas.length > 0) return 'building'
  return 'empty'
})

const statusLabel = computed(() => {
  if (reportState.value === 'failed') return t('growthReport.failedState')
  if (reportState.value === 'demo') return t('growthReport.demoState')
  if (reportState.value === 'ready') return t('growthReport.readyState')
  if (reportState.value === 'building') return t('growthReport.buildingState')
  return t('growthReport.emptyState')
})

const statusTagType = computed(() => {
  if (reportState.value === 'failed') return 'danger'
  if (reportState.value === 'demo') return 'warning'
  if (reportState.value === 'ready') return 'success'
  if (reportState.value === 'building') return 'info'
  return 'info'
})

const latestGrowthAt = computed(() => {
  const timestamps = [...props.confirmedMemories, ...props.tasks]
    .map((item) => item.created_at)
    .filter((item): item is string => Boolean(item))
    .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())
  return timestamps[0] || ''
})

const learnedInsights = computed(() => props.confirmedMemories.slice(0, 3).map((item) => ({
  id: item.id,
  content: item.content,
  evidence: item.task_id || t('growthReport.directConfirmation'),
  created_at: item.created_at,
})))

const improvementItems = computed(() => {
  const items: string[] = []
  if (currentPersona.value) {
    items.push(t('growthReport.improvementPersona', { version: currentPersona.value.version }))
  }
  if (props.confirmedMemories.length > 0) {
    items.push(t('growthReport.improvementConfirmed', { count: props.confirmedMemories.length }))
  }
  if (props.tasks.length > 0) {
    items.push(t('growthReport.improvementTasks', { count: props.tasks.length }))
  }
  if (items.length === 0) {
    items.push(t('growthReport.improvementEmpty'))
  }
  return items
})

const nextActions = computed(() => {
  const actions: Array<{ label: string; to: string }> = []
  if (props.pendingMemories.length > 0) {
    actions.push({ label: t('growthReport.actionReviewPending', { count: props.pendingMemories.length }), to: '/memories' })
  }
  if (!currentPersona.value) {
    actions.push({ label: t('growthReport.actionGeneratePersona'), to: '/persona' })
  }
  if (props.tasks.length === 0) {
    actions.push({ label: t('growthReport.actionRunTask'), to: '/tasks' })
  }
  if (props.confirmedMemories.length > 0) {
    actions.push({ label: t('growthReport.actionInspectEvidence'), to: '/audit' })
  }
  return actions.slice(0, 3)
})

const traceabilityDescription = computed(() => {
  if (reportState.value === 'failed') {
    return t('growthReport.failedTraceability')
  }
  if (props.confirmedMemories.length === 0) {
    return t('growthReport.traceabilityEmpty')
  }
  const evidence = learnedInsights.value
    .map((item) => item.evidence)
    .slice(0, 3)
    .join(' · ')
  return t('growthReport.traceabilityDescription', { evidence })
})

const formatDate = (value: string) => new Date(value).toLocaleString()
</script>

<style scoped>
.growth-report-card {
  border: 1px solid #e5e7eb;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.report-header h3 {
  margin: 4px 0 0;
}

.eyebrow {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.snapshot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.snapshot-item {
  padding: 12px;
  border-radius: 12px;
  background: #f8fafc;
}

.snapshot-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 6px;
}

.snapshot-value {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.snapshot-date {
  font-size: 14px;
}

.report-section {
  margin-bottom: 16px;
}

.section-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.section-title-row h4,
.report-subcard h4 {
  margin: 0;
}

.insight-list {
  display: grid;
  gap: 10px;
}

.insight-item {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #fff;
}

.insight-content {
  color: #111827;
  margin-bottom: 8px;
  line-height: 1.5;
}

.insight-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.report-subcard {
  height: 100%;
}

.bullet-list {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 8px;
  color: #374151;
}

.action-list {
  padding-left: 0;
  list-style: none;
}

.action-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
</style>
