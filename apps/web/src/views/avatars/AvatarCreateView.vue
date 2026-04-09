<template>
  <section class="page-card page-grid">
    <h2>{{ t('avatarCreate.title') }}</h2>
    <div class="form-grid">
      <el-input v-model="name" :placeholder="t('avatarCreate.namePlaceholder')" />
      <el-input v-model="goal" type="textarea" :rows="4" :placeholder="t('avatarCreate.goalPlaceholder')" />
      <el-select v-model="visibility">
        <el-option :label="t('avatarCreate.private')" value="private" />
        <el-option :label="t('avatarCreate.team')" value="team" />
      </el-select>
      <el-button type="primary" @click="submit">{{ t('avatarCreate.create') }}</el-button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAvatarStore } from '../../stores/avatar'

const { t } = useI18n()
const router = useRouter()
const avatarStore = useAvatarStore()
const name = ref('Demo Avatar')
const goal = ref('Help manage a digital identity and complete safe tasks.')
const visibility = ref('private')

const submit = async () => {
  await avatarStore.create({ name: name.value, goal: goal.value, visibility: visibility.value })
  ElMessage.success(t('avatarCreate.created'))
  await router.push('/avatars')
}
</script>
