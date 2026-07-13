import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { IndexData, BarData } from '../types/stock'
import { fetchIndices, fetchIndexBars, fetchMarketStatus } from '../api'
import { useWebSocket, type ConnectionStatus } from '../composables/useWebSocket'

export const useStockStore = defineStore('stock', () => {
  const indices = ref<IndexData[]>([])
  const indexBars = ref<BarData[]>([])
  const loading = ref(false)
  const isTrading = ref(false)
  const pollingInterval = ref(5000)
  const wsStatus = ref<ConnectionStatus>('disconnected')
  let _pollTimer: ReturnType<typeof setInterval> | null = null
  let _ws: ReturnType<typeof useWebSocket> | null = null
  let _usePolling = ref(false)

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

  function startWebSocket(codes: string[] = []) {
    _ws = useWebSocket({
      codes,
      onQuoteUpdate(data) {
        // Quote updates come from WebSocket
      },
      onIndexUpdate(data) {
        indices.value = data.map((item: any) => ({
          code: item.code,
          name: item.name,
          price: item.price,
          change: item.change,
          change_pct: item.change_pct,
        }))
      },
    })
    _ws.connect()
    wsStatus.value = _ws.status.value
  }

  function stopWebSocket() {
    _ws?.disconnect()
    _ws = null
    wsStatus.value = 'disconnected'
  }

  return {
    indices,
    indexBars,
    loading,
    isTrading,
    pollingInterval,
    wsStatus,
    loadIndices,
    loadIndexBars,
    checkMarketStatus,
    startPolling,
    stopPolling,
    startWebSocket,
    stopWebSocket,
  }
}
