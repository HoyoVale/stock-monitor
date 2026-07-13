<template>
  <div>
    <n-card
      :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d', marginBottom: '16px' }"
      :bordered="false"
    >
      <template #header>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <span style="color: #e6edf3; font-weight: 600;">
            {{ stockCode }}
            <span v-if="stockName" style="color: #8b949e; font-weight: 400; margin-left: 4px;">{{ stockName }}</span>
          </span>
          <n-tag :type="trendTagType" size="small">{{ result.trend }}</n-tag>
        </div>
      </template>

      <!-- 指标概览 -->
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
        <div>
          <div style="font-size: 11px; color: #8b949e; margin-bottom: 2px;">当前价格</div>
          <div style="font-size: 24px; font-weight: 700; color: #e6edf3;">{{ result.last_price }}</div>
        </div>
        <div>
          <div style="font-size: 11px; color: #8b949e; margin-bottom: 2px;">方向准确率</div>
          <div style="font-size: 24px; font-weight: 700; color: #f0b90b;">{{ result.metrics.direction_accuracy_pct }}%</div>
        </div>
        <div>
          <div style="font-size: 11px; color: #8b949e; margin-bottom: 2px;">预测 {{ days }} 日后</div>
          <div :style="{ fontSize: '24px', fontWeight: 700, color: finalChange >= 0 ? '#e74c3c' : '#2ecc71' }">
            {{ finalPrice }}
          </div>
        </div>
      </div>

      <!-- 预测图表 -->
      <div ref="miniChartRef" style="width: 100%; height: 200px; margin-bottom: 12px;"></div>

      <!-- 预测明细表格 -->
      <n-data-table
        :columns="columns"
        :data="result.predictions"
        :bordered="false"
        size="small"
        :max-height="200"
      />

      <!-- 缓存状态 -->
      <div
        v-if="result.cache_hit"
        style="margin-top: 8px; font-size: 11px; color: #8b949e; text-align: right;"
      >
        ⚡ 模型缓存命中
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, nextTick, type PropType } from 'vue'
import { NCard, NTag, NDataTable } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import * as echarts from 'echarts'
import type { PredictionResult } from '../api'

const props = defineProps({
  stockCode: { type: String, required: true },
  stockName: { type: String, default: '' },
  result: { type: Object as PropType<PredictionResult>, required: true },
  days: { type: Number, default: 7 },
})

const finalPrice = computed(() => {
  if (!props.result.predictions.length) return '--'
  return props.result.predictions[props.result.predictions.length - 1].price.toFixed(2)
})

const finalChange = computed(() => {
  if (!props.result.predictions.length) return 0
  return props.result.predictions[props.result.predictions.length - 1].price - props.result.last_price
})

const trendTagType = computed(() => (props.result.trend === '上涨' ? 'error' : 'success'))

const columns: DataTableColumns<any> = [
  { title: '日期', key: 'date', width: 100 },
  {
    title: '预测价',
    key: 'price',
    width: 80,
    render: (row: any) => `${row.price}`,
  },
  {
    title: '区间',
    key: 'range',
    width: 140,
    render: (row: any) => `${row.lower} ~ ${row.upper}`,
  },
]

const miniChartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

function renderMiniChart() {
  if (!miniChartRef.value || !props.result.predictions.length) return

  if (!chartInstance) {
    chartInstance = echarts.init(miniChartRef.value)
  }

  const preds = props.result.predictions
  const dates = preds.map((p) => p.date)
  const prices = preds.map((p) => p.price)
  const lowers = preds.map((p) => p.lower)
  const uppers = preds.map((p) => p.upper)

  chartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 16, top: 12, bottom: 24 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { color: '#8b949e', fontSize: 9 },
      axisLine: { lineStyle: { color: '#30363d' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#8b949e', fontSize: 9 },
      splitLine: { lineStyle: { color: '#21262d' } },
      scale: true,
    },
    series: [
      {
        name: '置信区间上界',
        type: 'line',
        data: uppers,
        lineStyle: { opacity: 0 },
        areaStyle: { color: 'rgba(240, 185, 11, 0.08)' },
        showSymbol: false,
        stack: 'confidence',
        silent: true,
      },
      {
        name: '置信区间下界',
        type: 'line',
        data: lowers,
        lineStyle: { opacity: 0 },
        areaStyle: { color: '#161b22' },
        showSymbol: false,
        stack: 'confidence',
        tooltip: { show: false },
        silent: true,
      },
      {
        name: '预测价格',
        type: 'line',
        data: prices,
        smooth: true,
        lineStyle: { color: '#f0b90b', width: 2 },
        itemStyle: { color: '#f0b90b' },
        symbol: 'circle',
        symbolSize: 5,
        markLine: {
          silent: true,
          data: [
            {
              yAxis: props.result.last_price,
              lineStyle: { color: '#58a6ff', type: 'dashed', width: 1 },
              label: { show: false },
            },
          ],
        },
      },
    ],
  })
}

watch(
  () => props.result,
  () => {
    nextTick(() => renderMiniChart())
  },
  { immediate: false },
)

onMounted(() => {
  nextTick(() => renderMiniChart())
})
</script>
