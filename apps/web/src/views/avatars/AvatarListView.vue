<template>
  <section class="page-card page-grid">
    <div class="actions">
      <el-button type="primary" @click="load">{{ t('avatars.refresh') }}</el-button>
    </div>
    <h2>{{ t('avatars.title') }}</h2>
    <div class="list-grid">
      <article v-for="avatar in avatarStore.items" :key="avatar.id" class="list-item">
        <template v-if="editingId === avatar.id">
          <el-input v-model="draft.name" :placeholder="t('avatars.namePlaceholder')" />
          <el-input v-model="draft.goal" type="textarea" :rows="3" :placeholder="t('avatars.goalPlaceholder')" />
          <el-select v-model="draft.visibility">
            <el-option :label="t('avatars.private')" value="private" />
            <el-option :label="t('avatars.team')" value="team" />
          </el-select>
        </template>
        <template v-else>
          <strong>{{ avatar.name }}</strong>
          <p>{{ avatar.goal }}</p>
          <small>{{ avatar.visibility }} · {{ avatar.status }}</small>
        </template>
        <div class="actions">
          <el-button size="small" @click="avatarStore.setCurrentAvatar(avatar.id)">{{ t('avatars.select') }}</el-button>
          <template v-if="editingId === avatar.id">
            <el-button size="small" type="success" @click="save">{{ t('avatars.save') }}</el-button>
            <el-button size="small" @click="cancelEdit">{{ t('avatars.cancel') }}</el-button>
          </template>
          <el-button v-else size="small" @click="startEdit(avatar)">{{ t('avatars.edit') }}</el-button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import type { AvatarResponse } from '../../types/generated/api'
import { useAvatarStore } from '../../stores/avatar'

const { t } = useI18n()
const avatarStore = useAvatarStore()
const editingId = ref('')
const draft = reactive({ name: '', goal: '', visibility: 'private' })

const load = () => avatarStore.fetchAll()

const startEdit = (avatar: AvatarResponse) => {
  editingId.value = avatar.id
  draft.name = avatar.name
  draft.goal = avatar.goal
  draft.visibility = avatar.visibility
}

const cancelEdit = () => {
  editingId.value = ''
}

const save = async () => {
  if (!editingId.value) return
  await avatarStore.update({ id: editingId.value, name: draft.name, goal: draft.goal, visibility: draft.visibility })
  editingId.value = ''
  ElMessage.success(t('avatars.updated'))
}

onMounted(load)
</script>
