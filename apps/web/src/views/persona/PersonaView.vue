<template>
  <section class="page-card page-grid">
    <h2>{{ t('persona.title') }}</h2>
    <div class="form-grid">
      <el-input v-model="samples" type="textarea" :rows="6" :placeholder="t('persona.samplePlaceholder')" />
      <el-button type="primary" @click="generate" :disabled="!resolvedAvatarId">{{ t('persona.generate') }}</el-button>
    </div>
    <div class="list-grid">
      <article v-for="persona in workspace.personas" :key="persona.id" class="list-item persona-card">
        <div class="persona-header">
          <strong>v{{ persona.version }}</strong>
          <div class="persona-badges">
            <el-tag v-if="persona.is_current" type="success" size="small">{{ t('persona.active') }}</el-tag>
            <el-tag v-else type="info" size="small">{{ t('persona.inactive') }}</el-tag>
          </div>
        </div>
        <p>{{ persona.summary }}</p>
        <small>{{ persona.source_count }} {{ t('persona.sources') }} · {{ formatDate(persona.created_at) }}</small>
        <div class="actions" v-if="!persona.is_current">
          <el-button size="small" type="success" @click="activate(persona.id)">{{ t('persona.activate') }}</el-button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useAvatarStore } from '../../stores/avatar'
import { useWorkspaceStore } from '../../stores/workspace'

const { t } = useI18n()
const route = useRoute()
const avatarStore = useAvatarStore()
const workspace = useWorkspaceStore()
const samples = ref('I prefer concise updates.\nI want safe, traceable automation.')

const resolvedAvatarId = computed(() => {
  const routeAvatarId = route.params.avatarId
  return typeof routeAvatarId === 'string' && routeAvatarId ? routeAvatarId : avatarStore.currentAvatarId
})

const formatDate = (d: string) => new Date(d).toLocaleString()

const load = async () => {
  if (!resolvedAvatarId.value) return
  avatarStore.setCurrentAvatar(resolvedAvatarId.value)
  await workspace.loadAvatarWorkspace(resolvedAvatarId.value)
}

const generate = async () => {
  if (!resolvedAvatarId.value) return
  await workspace.generatePersona(resolvedAvatarId.value, samples.value.split('\n').filter(Boolean))
  ElMessage.success(t('persona.generated'))
}

const activate = async (personaId: string) => {
  await workspace.activatePersona(personaId, resolvedAvatarId.value)
  ElMessage.success(t('persona.activated'))
}

watch(resolvedAvatarId, load)
onMounted(load)
</script>

<style scoped>
.persona-card { transition: transform 0.15s; }
.persona-card:hover { transform: translateY(-1px); }
.persona-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.persona-badges { display: flex; gap: 4px; }
</style>
