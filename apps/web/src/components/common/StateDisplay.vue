<template>
  <div class="state-display">
    <!-- Loading -->
    <div v-if="loading" class="state-loading">
      <el-skeleton :animated="true" :count="skeletonCount" />
    </div>

    <!-- Error with retry -->
    <div v-else-if="error" class="state-error">
      <el-result icon="error" :title="errorTitle" :sub-title="error">
        <template #extra>
          <el-button type="primary" @click="$emit('retry')">{{ t('common.retry') }}</el-button>
        </template>
      </el-result>
    </div>

    <!-- Empty state -->
    <div v-else-if="empty" class="state-empty">
      <el-empty :description="emptyText">
        <slot name="empty-action" />
      </el-empty>
    </div>

    <!-- Has content -->
    <slot v-else />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{
  loading: boolean
  error: string | null
  empty: boolean
  emptyText?: string
  errorTitle?: string
  skeletonCount?: number
}>()

defineEmits<{
  retry: []
}>()

const { t } = useI18n()
</script>

<style scoped>
.state-display {
  width: 100%;
}

.state-loading,
.state-error,
.state-empty {
  padding: 24px;
  text-align: center;
}
</style>
