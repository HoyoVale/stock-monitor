<template>
  <div v-if="quote">
    <h2 style="color: #e6edf3; font-size: 18px; margin-bottom: 20px;">{{ quote.name }} ({{ quote.code }})</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">
      <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false">
        <div style="font-size: 32px; font-weight: 700;" :style="{ color: quote.change >= 0 ? '#e74c3c' : '#2ecc71' }">
          {{ quote.price?.toFixed(2) }}
          <span style="font-size: 16px; margin-left: 8px;">{{ quote.change >= 0 ? '+' : '' }}{{ quote.change?.toFixed(2) }} ({{ quote.change_pct >= 0 ? '+' : '' }}{{ quote.change_pct?.toFixed(2) }}%)</span>
        </div>
      </n-card>
      <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 14px; color: #c9d1d9;">
          <div>开盘: <span style="font-family: monospace;">{{ quote.open?.toFixed(2) }}</span></div>
          <div>最高: <span style="font-family: monospace;">{{ quote.high?.toFixed(2) }}</span></div>
          <div>最低: <span style="font-family: monospace;">{{ quote.low?.toFixed(2) }}</span></div>
          <div>成交量: <span style="font-family: monospace;">{{ quote.volume }}</span></div>
        </div>
      </n-card>
    </div>
    <h3 style="color: #e6edf3; margin-bottom: 12px; font-size: 16px;">K 线图</h3>
    <KLineChart :data="bars" style="margin-bottom: 24px;" />
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
      <div>
        <h3 style="color: #e6edf3; margin-bottom: 12px; font-size: 16px;">技术指标</h3>
        <IndicatorPanel :indicators="indicatorList" />
      </div>
      <DecisionCard v-if="suggestion" :data="suggestion" />
    </div>
  </div>
  <div v-else style="text-align: center; padding: 60px; color: #8b949e;">加载中...</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { NCard } from 'naive-ui'
import KLineChart from '../components/KLineChart.vue'
import IndicatorPanel from '../components/IndicatorPanel.vue'
import DecisionCard from '../components/DecisionCard.vue'
import { fetchStockQuote, fetchStockBars, fetchIndicators, fetchSuggestion } from '../api'
import type { QuoteData, BarData } from '../types/stock'

const route = useRoute()
const quote = ref<QuoteData | null>(null)
const bars = ref<BarData[]>([])
const indicatorResult = ref<any>({ indicators: [] })
const suggestion = ref<any>(null)

const indicatorList = computed(() => {
  return (indicatorResult.value?.indicators || indicatorResult.value || []).map((ind: any) => ({
    name: ind.name,
    signal: ind.signal || 'neutral',
    judgment: ind.judgment || '观望',
    weight: ind.weight || 0,
    raw_value: ind.values || ind.raw_value || {},
  }))
})

async function load(code: string) {
  quote.value = await fetchStockQuote(code)
  bars.value = await fetchStockBars(code)
  try {
    indicatorResult.value = await fetchIndicators(code)
    suggestion.value = await fetchSuggestion(code, quote.value?.name || '')
  } catch {}
}

onMounted(() => load(route.params.code as string))
watch(() => route.params.code, (c) => load(c as string))
</script>
