<template>
  <section class="page-card page-grid">
    <h2>{{ t('agents.title') }}</h2>
    <div class="form-grid">
      <el-input v-model="name" :placeholder="t('agents.namePlaceholder')" />
      <el-input v-model="rolePrompt" type="textarea" :rows="4" :placeholder="t('agents.rolePromptPlaceholder')" />
      <el-button type="primary" @click="create" :disabled="!resolvedAvatarId">{{ t('agents.create') }}</el-button>
    </div>
    <div class="list-grid">
      <article v-for="agent in workspace.agents" :key="agent.id" class="list-item">
        <strong>{{ agent.name }}</strong>
        <p>{{ agent.role_prompt }}</p>
        <small>{{ agent.status }}</small>
        <div class="actions">
          <el-button
            size="small"
            :type="agent.status === 'disabled' ? 'success' : 'warning'"
            @click="toggleStatus(agent.id, agent.status)"
          >
            {{ agent.status === 'disabled' ? t('agents.enable') : t('agents.disable') }}
          </el-button>
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
const name = ref('General Task Agent')
const rolePrompt = ref('Execute user tasks safely with persona context and policy awareness.')

const resolvedAvatarId = computed(() => {
  const routeAvatarId = route.params.avatarId
  return typeof routeAvatarId === 'string' && routeAvatarId ? routeAvatarId : avatarStore.currentAvatarId
})

const load = async () => {
  if (!resolvedAvatarId.value) return
  avatarStore.setCurrentAvatar(resolvedAvatarId.value)
  await workspace.loadAvatarWorkspace(resolvedAvatarId.value)
}

const create = async () => {
  if (!resolvedAvatarId.value) return
  await workspace.createAgent(resolvedAvatarId.value, { name: name.value, role_prompt: rolePrompt.value, permissions: ['task:run'] })
  ElMessage.success(t('agents.created'))
}

const toggleStatus = async (agentId: string, agentStatus: string) => {
  if (!resolvedAvatarId.value) return
  const nextStatus = agentStatus === 'disabled' ? 'ready' : 'disabled'
  await workspace.updateAgentStatus(agentId, nextStatus)
  ElMessage.success(nextStatus === 'disabled' ? t('agents.disabled') : t('agents.enabled'))
}

watch(resolvedAvatarId, load)
onMounted(load)
</script>
