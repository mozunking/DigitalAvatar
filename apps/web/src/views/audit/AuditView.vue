<template>
  <section class="page-card page-grid">
    <h2>{{ t('audit.title') }}</h2>
    <div class="filter-bar">
      <el-input v-model="filters.trace_id" :placeholder="t('audit.traceIdPlaceholder')" clearable class="filter-input" />
      <el-select v-model="filters.resource_type" :placeholder="t('audit.resourceTypePlaceholder')" clearable class="filter-select">
        <el-option label="Avatar" value="avatar" />
        <el-option label="Agent" value="agent" />
        <el-option label="Task" value="task" />
        <el-option label="Memory" value="memory" />
        <el-option label="Persona" value="persona" />
      </el-select>
      <el-date-picker v-model="filters.dateRange" type="datetimerange" :start-placeholder="t('audit.startAt')" :end-placeholder="t('audit.endAt')" value-format="YYYY-MM-DDTHH:mm:ss" />
      <el-button type="primary" @click="loadLogs">{{ t('audit.filter') }}</el-button>
      <el-button @click="resetFilters">{{ t('audit.reset') }}</el-button>
    </div>

    <el-empty v-if="workspace.auditLogs.length === 0" :description="t('audit.noLogs')" />
    <div v-else class="list-grid">
      <article v-for="item in workspace.auditLogs" :key="item.id" class="list-item audit-item">
        <div class="audit-header">
          <strong>{{ item.action }}</strong>
          <el-tag :type="item.result === 'success' ? 'success' : 'warning'" size="small">{{ item.result }}</el-tag>
        </div>
        <p class="audit-summary">{{ item.request_summary }}</p>
        <div class="audit-meta">
          <small>trace_id: {{ item.trace_id }}</small>
          <small>{{ item.resource_type }} / {{ item.resource_id.slice(0, 8) }}...</small>
          <small>{{ formatDate(item.created_at) }}</small>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWorkspaceStore } from '../../stores/workspace'

const { t } = useI18n()
const workspace = useWorkspaceStore()

const filters = reactive({
  trace_id: '',
  resource_type: '',
  dateRange: null as [string, string] | null,
})

const formatDate = (d: string) => new Date(d).toLocaleString()

const loadLogs = () => {
  workspace.loadAuditLogs({
    ...(filters.trace_id ? { trace_id: filters.trace_id } : {}),
    ...(filters.resource_type ? { resource_type: filters.resource_type } : {}),
    ...(filters.dateRange ? { start_at: filters.dateRange[0], end_at: filters.dateRange[1] } : {}),
  })
}

const resetFilters = () => {
  filters.trace_id = ''
  filters.resource_type = ''
  filters.dateRange = null
  loadLogs()
}

onMounted(loadLogs)
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.filter-input { width: 200px; }
.filter-select { width: 150px; }
.audit-item { transition: transform 0.15s; }
.audit-item:hover { transform: translateY(-1px); }
.audit-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.audit-summary { font-size: 0.875rem; color: #374151; margin: 4px 0; }
.audit-meta { display: flex; gap: 12px; color: #9ca3af; font-size: 0.75rem; }
</style>
