<template>
  <div>
    <h2 style="color: #e6edf3; margin-bottom: 20px; font-size: 18px;">AI 股价预测</h2>

    <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d', marginBottom: '20px' }" :bordered="false">
      <template #header><span style="color: #e6edf3; font-weight: 600;">预测参数</span></template>
      <n-space :size="12" align="center">
        <n-input v-model:value="stockCode" placeholder="股票代码 (如 600519)" style="width: 200px;" />
        <n-input-number v-model:value="days" :min="1" :max="30" :step="1" style="width: 160px;" placeholder="预测天数" />
        <n-button type="primary" @click="handlePredict" :loading="loading">
          {{ loading ? '预测中...' : '开始预测' }}
        </n-button>
      </n-space>
    </n-card>

    <n-alert v-if="errorMsg" type="error" style="margin-bottom: 20px;">{{ errorMsg }}</n-alert>

    <template v-if="result">
      <h3 style="color: #e6edf3; margin: 20px 0 12px; font-size: 16px;">
        {{ result.stock_code }} 预测结果
      </h3>

      <!-- 指标卡片 -->
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">当前价格</div>
          <div style="font-size: 28px; font-weight: 700; color: #e6edf3;">{{ result.last_price }}</div>
        </n-card>
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">趋势</div>
          <div :style="{ fontSize: '28px', fontWeight: 700, color: result.trend === '上涨' ? '#e74c3c' : '#2ecc71' }">
            {{ result.trend }}
          </div>
        </n-card>
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">方向准确率</div>
          <div style="font-size: 28px; font-weight: 700; color: '#f0b90b';">{{ result.metrics.direction_accuracy_pct }}%</div>
        </n-card>
      </div>

      <!-- 预测图表 -->
      <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false" style="margin-bottom: 20px;">
        <template #header><span style="color: #e6edf3; font-weight: 600;">预测曲线 (含置信区间)</span></template>
        <div ref="chartRef" style="width: 100%; height: 400px;"></div>
      </n-card>

      <!-- 预测表格 -->
      <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false" style="margin-bottom: 20px;">
        <template #header><span style="color: #e6edf3; font-weight: 600;">预测明细</span></template>
        <n-data-table :columns="columns" :data="result.predictions" :bordered="false" size="small" />
      </n-card>

      <!-- 模型指标 -->
      <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false">
        <template #header><span style="color: #e6edf3; font-weight: 600;">模型评估指标</span></template>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
          <div>
            <span style="color: #8b949e; font-size: 12px;">RMSE</span>
            <div style="color: #e6edf3; font-weight: 600;">{{ result.metrics.rmse }}</div>
          </div>
          <div>
            <span style="color: #8b949e; font-size: 12px;">MAE</span>
            <div style="color: #e6edf3; font-weight: 600;">{{ result.metrics.mae }}</div>
          </div>
          <div>
            <span style="color: #8b949e; font-size: 12px;">MAPE</span>
            <div style="color: #e6edf3; font-weight: 600;">{{ result.metrics.mape_pct }}%</div>
          </div>
          <div>
            <span style="color: #8b949e; font-size: 12px;">训练样本</span>
            <div style="color: #e6edf3; font-weight: 600;">{{ result.metrics.training_samples }}</div>
          </div>
        </div>
      </n-card>
    </template>

    <div v-else-if="!loading" style="text-align: center; padding: 40px; color: #8b949e;">
      输入股票代码和预测天数，查看 AI 预测结果
    </div>
  </div>
</template>

<script setup lang="ts">
import { h, ref, nextTick } from 'vue'
import { NCard, NInput, NInputNumber, NButton, NSpace, NDataTable, NAlert } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import * as echarts from 'echarts'
import { http, type PredictionResult } from '../api'

const cardStyle = {
  background: '#161b22',
  borderRadius: '12px',
  border: '1px solid #30363d',
}

const stockCode = ref('600519')
const days = ref(7)
const loading = ref(false)
const result = ref<PredictionResult | null>(null)
const errorMsg = ref('')
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const columns: DataTableColumns<any> = [
  { title: '日期', key: 'date', width: 120 },
  { title: '预测价格', key: 'price', width: 100 },
  { title: '下限', key: 'lower', width: 100 },
  { title: '上限', key: 'upper', width: 100 },
]

function renderChart() {
  if (!result.value || !chartRef.value) return
  const preds = result.value.predictions
  if (!preds.length) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const dates = preds.map((p: any) => p.date)
  const prices = preds.map((p: any) => p.price)
  const lowers = preds.map((p: any) => p.lower)
  const uppers = preds.map((p: any) => p.upper)

  chartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: 70, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { color: '#8b949e', fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#8b949e' },
      splitLine: { lineStyle: { color: '#21262d' } },
    },
    series: [
      {
        name: '置信区间',
        type: 'line',
        data: uppers,
        lineStyle: { opacity: 0 },
        areaStyle: { color: 'rgba(240, 185, 11, 0.1)' },
        showSymbol: false,
        stack: 'confidence',
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
      },
      {
        name: '预测价格',
        type: 'line',
        data: prices,
        smooth: true,
        lineStyle: { color: '#f0b90b', width: 2 },
        itemStyle: { color: '#f0b90b' },
        symbol: 'circle',
        symbolSize: 6,
      },
    ],
  })
}

async function handlePredict() {
  if (!stockCode.value || !days.value) return
  loading.value = true
  errorMsg.value = ''
  result.value = null

  try {
    const { data } = await http.post(`/predictions/${stockCode.value}`, { days: days.value })
    result.value = data
    await nextTick()
    renderChart()
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || err?.message || '预测失败'
  } finally {
    loading.value = false
  }
}
</script>
