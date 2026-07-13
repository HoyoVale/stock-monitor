<template>
  <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d', cursor: 'pointer' }" :bordered="false" @click="showModal = true">
    <template #header><span style="color: #e6edf3; font-weight: 600;">决策建议</span></template>
    <div style="text-align: center;">
      <div style="font-size: 36px; font-weight: 700; color: #f0b90b;">{{ data.rating || '暂无数据' }}</div>
      <div style="font-size: 28px; font-weight: 700; color: #e6edf3; margin: 4px 0;">{{ data.overall_score }}<span style="font-size: 14px; color: #8b949e;">/100</span></div>
      <n-tag :type="scoreColor(data.overall_score)" round>{{ data.rating_label }}</n-tag>
      <div style="font-size: 12px; color: #8b949e; margin-top: 8px; line-height: 1.6;">{{ data.summary }}</div>
    </div>
  </n-card>

  <n-modal v-model:show="showModal" preset="card" title="综合决策分析报告" style="width: 720px; max-height: 80vh;" transform-origin="center">
    <div v-if="data.data_source" style="margin-bottom: 20px; padding: 12px; background: #21262d; border-radius: 8px;">
      <div style="font-size: 13px; font-weight: 600; color: #f0b90b; margin-bottom: 6px;">数据来源</div>
      <div style="font-size: 12px; color: #8b949e; line-height: 1.6;" v-for="(v, k) in data.data_source" :key="k">
        {{ k }}: {{ v }}
      </div>
    </div>
    <div v-for="ind in (data.indicators || [])" :key="ind.name" style="padding: 12px; margin-bottom: 8px; background: #0d1117; border-radius: 8px; border: 1px solid #21262d;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-weight: 600; color: #e6edf3;">{{ ind.name }}</span>
        <n-tag :type="signalType(ind.signal)" size="small" round>{{ ind.judgment }}</n-tag>
      </div>
      <div style="font-size: 12px; color: #8b949e; line-height: 1.8;">
        <div>原始值: {{ JSON.stringify(ind.raw_value) }}</div>
        <div>信号: {{ ind.signal }} | 权重: {{ ind.weight }}% | 贡献: {{ ind.score_contribution?.toFixed(1) }}</div>
        <div style="color: #c9d1d9; margin-top: 4px;">{{ ind.explanation }}</div>
      </div>
    </div>
    <div style="padding: 12px; margin-top: 12px; background: #0d1117; border-radius: 8px; border: 1px solid #30363d;">
      <div style="font-size: 12px; color: #8b949e;">仓位建议: <span style="color: #f0b90b; font-weight: 600;">{{ data.position_suggestion }}</span></div>
      <div style="font-size: 12px; color: #e74c3c; margin-top: 4px;">风险提示: {{ data.risk_tips }}</div>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { NCard, NTag, NModal } from 'naive-ui'

const props = defineProps<{
  data: {
    overall_score: number
    rating: string
    rating_label: string
    summary: string
    risk_tips: string
    position_suggestion: string
    data_source: Record<string, string>
    indicators: Array<{
      name: string
      signal: string
      judgment: string
      weight: number
      raw_value: Record<string, number>
      score_contribution: number
      explanation: string
    }>
  }
}>()

const showModal = ref(false)

function scoreColor(score: number) {
  if (score >= 60) return 'error'
  if (score >= 40) return 'default'
  return 'success'
}

function signalType(sig: string) {
  const map: Record<string, 'success' | 'error' | 'default'> = {
    golden_cross: 'success', oversold: 'success', price_below_lower: 'success', bullish: 'success',
    dead_cross: 'error', overbought: 'error', price_above_upper: 'error', bearish: 'error',
  }
  return map[sig] || 'default'
}
</script>
