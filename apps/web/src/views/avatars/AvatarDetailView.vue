<template>
  <section class="page-card page-grid">
    <div class="detail-header">
      <el-button @click="$router.push('/avatars')" text>{{ t('avatars.backToList') }}</el-button>
      <h2>{{ avatar?.name || t('avatars.loading') }}</h2>
      <div class="header-actions">
        <el-button v-if="!editing" size="small" @click="startEdit">{{ t('avatars.edit') }}</el-button>
        <template v-else>
          <el-button size="small" type="success" @click="save">{{ t('avatars.save') }}</el-button>
          <el-button size="small" @click="cancelEdit">{{ t('avatars.cancel') }}</el-button>
        </template>
      </div>
    </div>

    <el-skeleton :loading="loading" animated :count="1">
      <template #default>
        <template v-if="avatar">
          <!-- Avatar Info -->
          <el-card shadow="never" class="info-card">
            <template v-if="editing">
              <el-form label-position="top">
                <el-form-item :label="t('avatars.namePlaceholder')">
                  <el-input v-model="draft.name" />
                </el-form-item>
                <el-form-item :label="t('avatars.goalPlaceholder')">
                  <el-input v-model="draft.goal" type="textarea" :rows="3" />
                </el-form-item>
                <el-form-item :label="t('avatars.visibility')">
                  <el-select v-model="draft.visibility">
                    <el-option :label="t('avatars.private')" value="private" />
                    <el-option :label="t('avatars.team')" value="team" />
                  </el-select>
                </el-form-item>
              </el-form>
            </template>
            <template v-else>
              <el-descriptions :column="2" border>
                <el-descriptions-item :label="t('avatars.name')">{{ avatar.name }}</el-descriptions-item>
                <el-descriptions-item label="Status">
                  <el-tag :type="avatar.status === 'active' ? 'success' : 'info'" size="small">{{ avatar.status }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item :label="t('avatars.goal')" :span="2">{{ avatar.goal }}</el-descriptions-item>
                <el-descriptions-item label="Visibility">{{ avatar.visibility }}</el-descriptions-item>
                <el-descriptions-item label="Created">{{ formatDate(avatar.created_at) }}</el-descriptions-item>
              </el-descriptions>
            </template>
          </el-card>

          <GrowthReportCard
            :avatar-name="avatar.name"
            :personas="workspace.personas"
            :tasks="workspace.tasks"
            :pending-memories="workspace.memories"
            :confirmed-memories="workspace.confirmedMemories"
            :loading="workspace.loading"
            :failed="Boolean(workspace.workspaceError)"
          />

          <!-- Related Stats -->
          <div class="stats-grid">
            <el-card shadow="hover" class="stat-card" @click="$router.push('/persona')">
              <el-statistic :title="t('persona.title')" :value="workspace.personas.length" />
              <small v-if="workspace.personas.length > 0">{{ t('persona.active') }}: v{{ workspace.personas[0].version }}</small>
            </el-card>
            <el-card shadow="hover" class="stat-card" @click="$router.push('/agents')">
              <el-statistic :title="t('agents.title')" :value="workspace.agents.length" />
            </el-card>
            <el-card shadow="hover" class="stat-card" @click="$router.push('/tasks')">
              <el-statistic :title="t('tasks.title')" :value="workspace.tasks.length" />
            </el-card>
            <el-card shadow="hover" class="stat-card" @click="$router.push('/memories')">
              <el-statistic :title="t('memories.title')" :value="workspace.memories.length" />
            </el-card>
          </div>

          <!-- Recent Tasks -->
          <div v-if="workspace.tasks.length > 0">
            <h3>{{ t('dashboard.recentTasks') }}</h3>
            <div class="list-grid">
              <article v-for="task in workspace.tasks.slice(0, 5)" :key="task.task_id" class="list-item">
                <el-tag :type="taskStatusType(task.status)" size="small">{{ task.status }}</el-tag>
                <p class="task-text">{{ task.result || task.error || task.status }}</p>
                <small>trace_id: {{ task.trace_id }}</small>
              </article>
            </div>
          </div>
        </template>

        <el-empty v-else :description="t('avatars.notFound')">
          <el-button type="primary" @click="$router.push('/avatars')">{{ t('avatars.backToList') }}</el-button>
        </el-empty>
      </template>
    </el-skeleton>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import GrowthReportCard from '../../components/common/GrowthReportCard.vue'
import { avatarApi } from '../../api'
import type { AvatarResponse } from '../../types/generated/api'
import { useAvatarStore } from '../../stores/avatar'
import { useWorkspaceStore } from '../../stores/workspace'

const { t } = useI18n()
const route = useRoute()
const avatarStore = useAvatarStore()
const workspace = useWorkspaceStore()

const loading = ref(true)
const editing = ref(false)
const avatar = ref<AvatarResponse | null>(null)
const draft = reactive({ name: '', goal: '', visibility: 'private' })

const avatarId = computed(() => route.params.id as string)

const taskStatusType = (status: string) => {
  const map: Record<string, string> = { succeeded: 'success', failed: 'danger', blocked: 'warning', running: '', pending: 'info' }
  return map[status] || 'info'
}

const formatDate = (d: string) => new Date(d).toLocaleString()

const load = async () => {
  loading.value = true
  try {
    const { data } = await avatarApi.get(avatarId.value)
    avatar.value = data
    avatarStore.setCurrentAvatar(avatarId.value)
    await workspace.loadAvatarWorkspace(avatarId.value)
    await workspace.loadPendingMemories()
  } catch {
    avatar.value = null
  } finally {
    loading.value = false
  }
}

const startEdit = () => {
  if (!avatar.value) return
  editing.value = true
  draft.name = avatar.value.name
  draft.goal = avatar.value.goal
  draft.visibility = avatar.value.visibility
}

const cancelEdit = () => {
  editing.value = false
}

const save = async () => {
  if (!avatarId.value) return
  try {
    const { data } = await avatarApi.update(avatarId.value, { name: draft.name, goal: draft.goal, visibility: draft.visibility })
    avatar.value = data
    editing.value = false
    ElMessage.success(t('avatars.updated'))
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.error?.message || t('avatars.updateFailed'))
  }
}

watch(() => route.params.id, load)
onMounted(load)
</script>

<style scoped>
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-header h2 {
  flex: 1;
  margin: 0;
}

.info-card {
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  cursor: pointer;
  text-align: center;
  transition: transform 0.15s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.task-text {
  font-size: 0.875rem;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 500px;
}
</style>

