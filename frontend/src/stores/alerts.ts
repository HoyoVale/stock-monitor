import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AlertRule, AlertRecord } from '../types/stock'
import {
  fetchAlertRules,
  createAlertRule,
  deleteAlertRule,
  toggleAlertRule,
  fetchAlertRecords,
  fetchUnreadAlertCount,
} from '../api'

export const useAlertStore = defineStore('alerts', () => {
  const rules = ref<AlertRule[]>([])
  const records = ref<AlertRecord[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)

  async function loadRules() {
    loading.value = true
    try {
      rules.value = await fetchAlertRules()
    } finally {
      loading.value = false
    }
  }

  async function loadRecords() {
    records.value = await fetchAlertRecords(50)
  }

  async function addRule(data: { stock_code: string; alert_type: string; threshold: number }) {
    const rule = await createAlertRule(data)
    rules.value.unshift(rule)
    return rule
  }

  async function removeRule(id: number) {
    await deleteAlertRule(id)
    rules.value = rules.value.filter((r) => r.id !== id)
  }

  async function toggleRule(id: number, enabled: boolean) {
    await toggleAlertRule(id, enabled)
    const rule = rules.value.find((r) => r.id === id)
    if (rule) rule.enabled = enabled
  }

  async function checkUnread() {
    try {
      unreadCount.value = await fetchUnreadAlertCount()
    } catch {
      // ignore
    }
  }

  return {
    rules,
    records,
    unreadCount,
    loading,
    loadRules,
    loadRecords,
    addRule,
    removeRule,
    toggleRule,
    checkUnread,
  }
})
