<template>
  <div class="auth-page">
    <n-card class="auth-card" :bordered="false">
      <template #header>
        <h2 style="color: #e6edf3; text-align: center; margin: 0;">注册</h2>
      </template>
      <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleRegister">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="form.username" placeholder="输入用户名 (字母数字下划线)" />
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="form.email" placeholder="输入邮箱地址" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input v-model:value="form.password" type="password" placeholder="至少6位" />
        </n-form-item>
        <n-form-item label="确认密码" path="confirmPassword">
          <n-input v-model:value="form.confirmPassword" type="password" placeholder="再次输入密码" />
        </n-form-item>
        <n-button
          type="primary"
          block
          :loading="authStore.loading"
          :disabled="authStore.loading"
          @click="handleRegister"
          style="margin-top: 8px;"
        >
          注册
        </n-button>
      </n-form>
      <div style="text-align: center; margin-top: 16px; color: #8b949e;">
        已有账号？
        <n-button text type="primary" @click="$router.push('/login')">立即登录</n-button>
      </div>
      <div v-if="registerError" style="text-align: center; color: #e74c3c; margin-top: 12px;">
        {{ registerError }}
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInst | null>(null)
const registerError = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validatePasswordsMatch = (_: any, value: string) => {
  if (value !== form.password) {
    return new Error('两次密码输入不一致')
  }
  return true
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度 3-20 位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '仅支持字母、数字和下划线', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePasswordsMatch, trigger: 'blur' },
  ],
}

async function handleRegister() {
  registerError.value = ''
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  try {
    await authStore.register(form.username, form.email, form.password)
    router.push('/')
  } catch (err: any) {
    registerError.value = err?.response?.data?.detail || '注册失败，请重试'
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #0d1117;
}
.auth-card {
  width: 400px;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
}
</style>
