<template>
  <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
    <n-card v-for="ind in props.indicators" :key="ind.name" :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false">
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <span style="font-size: 14px; font-weight: 600; color: #e6edf3;">{{ ind.name }}</span>
          <n-tag :type="signalType(ind.signal)" size="small" round>{{ sigLabel(ind.signal) }}</n-tag>
        </div>
      </template>
      <div style="font-size: 12px; color: #8b949e; line-height: 1.8;">
        <div v-for="(v, k) in ind.raw_value" :key="k" style="display: flex; justify-content: space-between;">
          <span>{{ k }}</span>
          <span style="font-family: 'SF Mono', monospace;">{{ typeof v === 'number' ? v.toFixed(4) : v }}</span>
        </div>
        <div style="margin-top: 6px; display: flex; justify-content: space-between; border-top: 1px solid #21262d; padding-top: 6px;">
          <span>{{ ind.judgment || ind.signal }}</span>
          <span style="color: #f0b90b;">{{ ind.weight }}%</span>
        </div>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { NCard, NTag } from 'naive-ui'

const props = defineProps<{
  indicators: Array<{
    name: string
    signal: string
    judgment: string
    weight: number
    raw_value: Record<string, number>
  }>
}>()

function signalType(sig: string) {
  const map: Record<string, 'success' | 'error' | 'default'> = {
    golden_cross: 'success', oversold: 'success', price_below_lower: 'success', bullish: 'success',
    dead_cross: 'error', overbought: 'error', price_above_upper: 'error', bearish: 'error',
  }
  return map[sig] || 'default'
}

function sigLabel(sig: string) {
  const map: Record<string, string> = {
    golden_cross: '金叉', dead_cross: '死叉',
    oversold: '超卖', overbought: '超买',
    bullish: '多头', bearish: '空头',
    price_above_upper: '超上轨', price_below_lower: '触下轨',
    price_in_band: '带内', neutral: '中性',
  }
  return map[sig] || sig
}
</script>
