import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '../types/auth'
import { loginApi, registerApi, refreshTokenApi, getMeApi } from '../api/auth'

const TOKEN_KEY = 'stock-monitor-token'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  function setToken(t: string) {
    token.value = t
    localStorage.setItem(TOKEN_KEY, t)
  }

  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  async function login(username: string, password: string) {
    loading.value = true
    try {
      const resp = await loginApi(username, password)
      setToken(resp.access_token)
      await fetchUser()
      return resp
    } finally {
      loading.value = false
    }
  }

  async function register(username: string, email: string, password: string) {
    loading.value = true
    try {
      const resp = await registerApi(username, email, password)
      setToken(resp.access_token)
      await fetchUser()
      return resp
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await getMeApi(token.value)
    } catch {
      clearAuth()
    }
  }

  async function refreshToken() {
    if (!token.value) return
    try {
      const resp = await refreshTokenApi(token.value)
      setToken(resp.access_token)
    } catch {
      clearAuth()
    }
  }

  function logout() {
    clearAuth()
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    register,
    fetchUser,
    refreshToken,
    logout,
  }
})
