import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { IndexData, BarData } from '../types/stock'
import { fetchIndices, fetchIndexBars } from '../api'

export const useStockStore = defineStore('stock', () => {
  const indices = ref<IndexData[]>([])
  const indexBars = ref<BarData[]>([])
  const loading = ref(false)

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

  return { indices, indexBars, loading, loadIndices, loadIndexBars }
})
