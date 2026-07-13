<template>
  <div class="auth-page">
    <n-card class="auth-card" :bordered="false">
      <template #header>
        <h2 style="color: #e6edf3; text-align: center; margin: 0;">登录</h2>
      </template>
      <n-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="form.username" placeholder="输入用户名" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input v-model:value="form.password" type="password" placeholder="输入密码" @keyup.enter="handleLogin" />
        </n-form-item>
        <n-button
          type="primary"
          block
          :loading="authStore.loading"
          :disabled="authStore.loading"
          @click="handleLogin"
          style="margin-top: 8px;"
        >
          登录
        </n-button>
      </n-form>
      <div style="text-align: center; margin-top: 16px; color: #8b949e;">
        还没有账号？
        <n-button text type="primary" @click="$router.push('/register')">立即注册</n-button>
      </div>
      <div v-if="loginError" style="text-align: center; color: #e74c3c; margin-top: 12px;">
        {{ loginError }}
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
const loginError = ref('')

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  loginError.value = ''
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  try {
    await authStore.login(form.username, form.password)
    router.push('/')
  } catch (err: any) {
    loginError.value = err?.response?.data?.detail || '登录失败，请检查用户名和密码'
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
