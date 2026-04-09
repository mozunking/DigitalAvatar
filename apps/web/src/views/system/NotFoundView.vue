<template>
  <section class="page-card page-grid">
    <h2>{{ t('notFound.title') }}</h2>
    <RouterLink to="/dashboard">{{ t('notFound.backToDashboard') }}</RouterLink>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>
