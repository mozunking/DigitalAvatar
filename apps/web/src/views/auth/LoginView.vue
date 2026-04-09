<template>
  <section class="login-page">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h1>{{ t('login.title') }}</h1>
          <el-tabs v-model="mode" class="mode-tabs">
            <el-tab-pane :label="t('login.loginTab')" name="login" />
            <el-tab-pane :label="t('login.registerTab')" name="register" />
          </el-tabs>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
        <el-form-item :label="t('login.email')" prop="email">
          <el-input v-model="form.email" :placeholder="t('login.emailPlaceholder')" :prefix-icon="Message" />
        </el-form-item>
        <el-form-item v-if="mode === 'register'" :label="t('login.displayName')" prop="displayName">
          <el-input v-model="form.displayName" :placeholder="t('login.displayNamePlaceholder')" :prefix-icon="User" />
        </el-form-item>
        <el-form-item :label="t('login.password')" prop="password">
          <el-input v-model="form.password" type="password" :placeholder="t('login.passwordPlaceholder')" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item v-if="mode === 'register'" :label="t('login.confirmPassword')" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" :placeholder="t('login.passwordPlaceholder')" show-password :prefix-icon="Lock" />
        </el-form-item>

        <el-button type="primary" native-type="submit" :loading="auth.loading" class="submit-btn">
          {{ mode === 'login' ? t('login.loginBtn') : t('login.registerBtn') }}
        </el-button>
      </el-form>

      <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon :closable="false" class="error-alert" />
    </el-card>
  </section>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Message, Lock, User } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()
const formRef = ref()
const mode = ref<'login' | 'register'>('login')
const errorMsg = ref('')

const form = reactive({
  email: '',
  password: '',
  displayName: '',
  confirmPassword: ''
})

const validateConfirm = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (mode.value === 'register' && value !== form.password) {
    callback(new Error(t('login.passwordMismatch')))
  } else {
    callback()
  }
}

const rules = computed(() => ({
  email: [{ required: true, type: 'email', message: t('login.emailRequired'), trigger: 'blur' }],
  password: [{ required: true, min: 6, message: t('login.passwordMin'), trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirm, trigger: 'blur' }]
}))

const submit = async () => {
  errorMsg.value = ''
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  try {
    if (mode.value === 'login') {
      await auth.login(form.email, form.password)
      ElMessage.success(t('login.loginSuccess'))
    } else {
      await auth.register(form.email, form.password, form.displayName || undefined)
      ElMessage.success(t('login.registerSuccess'))
    }
    await router.push('/dashboard')
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.error?.message || t('login.operationFailed')
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  max-width: 90vw;
}

.card-header h1 {
  margin: 0 0 8px 0;
  font-size: 1.5rem;
  text-align: center;
  color: #333;
}

.mode-tabs {
  margin-top: 8px;
}

.submit-btn {
  width: 100%;
  margin-top: 8px;
}

.error-alert {
  margin-top: 16px;
}
</style>
