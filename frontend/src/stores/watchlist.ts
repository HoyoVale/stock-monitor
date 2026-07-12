import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { WatchlistItem, QuoteData } from '../types/stock'
import { fetchWatchlist, addToWatchlist, removeFromWatchlist, fetchStockQuote } from '../api'

export const useWatchlistStore = defineStore('watchlist', () => {
  const items = ref<WatchlistItem[]>([])
  const quotes = ref<Map<string, QuoteData>>(new Map())
  const loading = ref(false)

  async function loadItems() {
    loading.value = true
    try {
      items.value = await fetchWatchlist()
      await refreshQuotes()
    } finally {
      loading.value = false
    }
  }

  async function addItem(code: string, name: string) {
    await addToWatchlist(code, name)
    await loadItems()
  }

  async function removeItem(id: number) {
    await removeFromWatchlist(id)
    await loadItems()
  }

  async function refreshQuotes() {
    for (const item of items.value) {
      try {
        const q = await fetchStockQuote(item.code)
        quotes.value.set(item.code, q)
      } catch {
        // ignore failed quote fetches
      }
    }
  }

  return { items, quotes, loading, loadItems, addItem, removeItem, refreshQuotes }
})
