<template>
  <n-auto-complete
    :value="query"
    :options="options"
    :loading="searching"
    placeholder="搜索股票代码或名称..."
    clear-after-select
    @update:value="handleInput"
    @select="handleSelect"
    class="stock-search"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NAutoComplete } from 'naive-ui'
import { fetchStocks } from '../api'
import type { StockInfo } from '../types/stock'

const router = useRouter()
const query = ref('')
const searching = ref(false)
const options = ref<Array<{ label: string; value: string }>>([])

let timer: ReturnType<typeof setTimeout> | null = null

function handleInput(val: string) {
  query.value = val
  if (timer) clearTimeout(timer)
  if (!val || val.length < 2) { options.value = []; return }
  timer = setTimeout(async () => {
    searching.value = true
    try {
      const results = await fetchStocks(val)
      options.value = results.map((s: StockInfo) => ({
        label: `${s.code} - ${s.name}`,
        value: s.code,
      }))
    } finally {
      searching.value = false
    }
  }, 300)
}

function handleSelect(code: string) {
  query.value = ''
  router.push({ name: 'stock-detail', params: { code } })
}
</script>

<style scoped>
.stock-search {
  width: 240px;
}

@media (max-width: 768px) {
  .stock-search {
    width: 100%;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .stock-search {
    width: 180px;
  }
}
</style>
