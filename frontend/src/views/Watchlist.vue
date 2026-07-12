<template>
  <div>
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
      <h2 style="color: #e6edf3; font-size: 18px; margin: 0;">我的自选股</h2>
      <n-button type="primary" @click="showSearch = true">+ 添加股票</n-button>
    </div>
    <StockTable :data="quoteList" :loading="store.loading" />
    <n-modal v-model:show="showSearch" title="搜索股票" preset="card" style="width: 500px;" transform-origin="center">
      <n-input v-model:value="searchQuery" placeholder="输入股票代码或名称搜索" clearable @input="handleSearch" />
      <n-list v-if="searchResults.length > 0" style="margin-top: 12px;">
        <n-list-item v-for="s in searchResults" :key="s.code">
          <span>{{ s.code }} - {{ s.name }}</span>
          <template #suffix>
            <n-button size="small" @click="handleAdd(s.code, s.name)">添加</n-button>
          </template>
        </n-list-item>
      </n-list>
      <n-empty v-else-if="searchQuery && searchResults.length === 0" description="未找到" style="margin-top: 12px;" />
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NButton, NModal, NInput, NList, NListItem, NEmpty } from 'naive-ui'
import StockTable from '../components/StockTable.vue'
import { useWatchlistStore } from '../stores/watchlist'
import { fetchStocks } from '../api'
import type { StockInfo } from '../types/stock'

const store = useWatchlistStore()
const showSearch = ref(false)
const searchQuery = ref('')
const searchResults = ref<StockInfo[]>([])

const quoteList = computed(() => {
  return store.items.map(item => ({
    code: item.code,
    name: item.name,
    price: store.quotes.get(item.code)?.price ?? 0,
    change: store.quotes.get(item.code)?.change ?? 0,
    change_pct: store.quotes.get(item.code)?.change_pct ?? 0,
    open: store.quotes.get(item.code)?.open ?? 0,
    high: store.quotes.get(item.code)?.high ?? 0,
    low: store.quotes.get(item.code)?.low ?? 0,
    volume: store.quotes.get(item.code)?.volume ?? 0,
    amount: store.quotes.get(item.code)?.amount ?? 0,
  }))
})

async function handleSearch() {
  if (!searchQuery.value) { searchResults.value = []; return }
  searchResults.value = await fetchStocks(searchQuery.value)
}

async function handleAdd(code: string, name: string) {
  await store.addItem(code, name)
  showSearch.value = false
  searchQuery.value = ''
  searchResults.value = []
}

onMounted(() => store.loadItems())
</script>
