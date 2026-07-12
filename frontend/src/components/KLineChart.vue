<template>
  <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
      <div style="display: flex; gap: 8px;">
        <n-button
          v-for="p in periods" :key="p.value"
          size="tiny"
          :secondary="period !== p.value"
          @click="$emit('period-change', p.value)"
        >{{ p.label }}</n-button>
      </div>
    </div>
    <v-chart :option="chartOption" style="height: 380px;" autoresize />
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NCard, NButton } from 'naive-ui'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { CandlestickChart, LineChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, DataZoomComponent } from 'echarts/components'
import type { BarData } from '../types/stock'

use([CanvasRenderer, CandlestickChart, LineChart, TooltipComponent, GridComponent, DataZoomComponent])

const props = defineProps<{
  data: BarData[]
  period?: string
}>()

defineEmits<{ 'period-change': [value: string] }>()

const periods = [
  { label: '1月', value: '1m' },
  { label: '3月', value: '3m' },
  { label: '6月', value: '6m' },
  { label: '1年', value: '1y' },
]

const chartOption = computed(() => {
  const d = props.data || []
  const dates = d.map(i => i.date?.slice(0, 10))
  const ohlc = d.map(i => [i.open, i.close, i.low, i.high])
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    grid: { left: '5%', right: '5%', bottom: '15%', top: '5%' },
    xAxis: { type: 'category', data: dates, axisLine: { lineStyle: { color: '#30363d' } }, axisLabel: { color: '#8b949e' } },
    yAxis: { type: 'value', scale: true, splitLine: { lineStyle: { color: '#21262d' } }, axisLabel: { color: '#8b949e' } },
    dataZoom: [{ type: 'inside', start: 0, end: 100 }],
    series: [
      {
        type: 'candlestick',
        data: ohlc,
        itemStyle: { color: '#e74c3c', color0: '#2ecc71', borderColor: '#e74c3c', borderColor0: '#2ecc71' },
      },
    ],
  }
})
</script>
