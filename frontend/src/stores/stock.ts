import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { IndexData, BarData } from '../types/stock'
import { fetchIndices, fetchIndexBars, fetchMarketStatus } from '../api'

export const useStockStore = defineStore('stock', () => {
  const indices = ref<IndexData[]>([])
  const indexBars = ref<BarData[]>([])
  const loading = ref(false)
  const isTrading = ref(false)
  const pollingInterval = ref(5000)
  let _pollTimer: ReturnType<typeof setInterval> | null = null

  async function loadIndices() {
    loading.value = true
    try {
      indices.value = await fetchIndices()
    } finally {
      loading.value = false
    }
  }

  async function loadIndexBars(code: string, period = '1y') {
    indexBars.value = await fetchIndexBars(code, period)
  }

  async function checkMarketStatus() {
    try {
      const status = await fetchMarketStatus()
      isTrading.value = status.is_trading
      pollingInterval.value = status.recommended_interval * 1000
    } catch {
      // 默认 30 秒
      pollingInterval.value = 30000
    }
  }

  function startPolling() {
    stopPolling()
    _pollTimer = setInterval(async () => {
      await loadIndices()
      await checkMarketStatus()
    }, pollingInterval.value)
  }

  function stopPolling() {
    if (_pollTimer) {
      clearInterval(_pollTimer)
      _pollTimer = null
    }
  }

  return {
    indices,
    indexBars,
    loading,
    isTrading,
    pollingInterval,
    loadIndices,
    loadIndexBars,
    checkMarketStatus,
    startPolling,
    stopPolling,
  }
})
