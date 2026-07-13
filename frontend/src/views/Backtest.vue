<template>
  <div>
    <h2 style="color: #e6edf3; margin-bottom: 20px; font-size: 18px;">历史回测</h2>

    <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d', marginBottom: '20px' }" :bordered="false">
      <template #header><span style="color: #e6edf3; font-weight: 600;">回测参数</span></template>
      <n-space vertical :size="12">
        <n-grid :cols="5" :x-gap="12">
          <n-gi>
            <n-input v-model:value="form.code" placeholder="股票代码" />
          </n-gi>
          <n-gi>
            <n-date-picker v-model:formatted-value="form.startDate" value-format="yyyy-MM-dd" type="date" placeholder="开始日期" style="width: 100%;" />
          </n-gi>
          <n-gi>
            <n-date-picker v-model:formatted-value="form.endDate" value-format="yyyy-MM-dd" type="date" placeholder="结束日期" style="width: 100%;" />
          </n-gi>
          <n-gi>
            <n-input-number v-model:value="form.threshold" :min="0" :max="100" :step="1" placeholder="买入阈值 (0-100)" style="width: 100%;" />
          </n-gi>
          <n-gi>
            <n-button type="primary" @click="handleRun" :loading="running" style="width: 100%;">开始回测</n-button>
          </n-gi>
        </n-grid>
      </n-space>
    </n-card>

    <!-- 错误提示 -->
    <n-alert v-if="errorMsg" type="error" style="margin-bottom: 20px;">{{ errorMsg }}</n-alert>

    <!-- 结果 -->
    <template v-if="result">
      <h3 style="color: #e6edf3; margin: 20px 0 12px; font-size: 16px;">
        {{ result.stock_code }} &nbsp;{{ result.start_date }} ~ {{ result.end_date }}
      </h3>

      <!-- 指标卡片 -->
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">累计收益率</div>
          <div :style="{ fontSize: '28px', fontWeight: 700, color: result.total_return >= 0 ? '#e74c3c' : '#2ecc71' }">
            {{ result.total_return >= 0 ? '+' : '' }}{{ result.total_return }}%
          </div>
        </n-card>
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">年化收益率</div>
          <div :style="{ fontSize: '28px', fontWeight: 700, color: result.annualized_return >= 0 ? '#e74c3c' : '#2ecc71' }">
            {{ result.annualized_return >= 0 ? '+' : '' }}{{ result.annualized_return }}%
          </div>
        </n-card>
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">胜率 ({{ result.winning_trades }}/{{ result.total_trades }})</div>
          <div style="font-size: 28px; font-weight: 700; color: #e6edf3;">{{ result.win_rate }}%</div>
        </n-card>
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">最大回撤</div>
          <div style="font-size: 28px; font-weight: 700; color: #2ecc71;">{{ result.max_drawdown }}%</div>
        </n-card>
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">夏普比率</div>
          <div style="font-size: 28px; font-weight: 700; color: #e6edf3;">{{ result.sharpe_ratio }}</div>
        </n-card>
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">总交易次数</div>
          <div style="font-size: 28px; font-weight: 700; color: #e6edf3;">{{ result.total_trades }}</div>
        </n-card>
        <n-card :style="cardStyle" :bordered="false" size="small">
          <div style="font-size: 12px; color: #8b949e;">盈利/亏损</div>
          <div style="font-size: 28px; font-weight: 700;">
            <span style="color: #e74c3c;">{{ result.winning_trades }}</span>
            <span style="color: #c9d1d9;"> / </span>
            <span style="color: #2ecc71;">{{ result.losing_trades }}</span>
          </div>
        </n-card>
      </div>

      <!-- 权益曲线图表 -->
      <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false" style="margin-bottom: 20px;">
        <template #header><span style="color: #e6edf3; font-weight: 600;">权益曲线</span></template>
        <div ref="chartRef" style="width: 100%; height: 400px;"></div>
      </n-card>

      <!-- 交易信号列表 -->
      <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false">
        <template #header><span style="color: #e6edf3; font-weight: 600;">交易信号</span></template>
        <n-data-table
          v-if="tradeSignals.length > 0"
          :columns="signalColumns"
          :data="tradeSignals"
          :bordered="false"
          size="small"
          :max-height="400"
          virtual-scroll
        />
        <div v-else style="color: #8b949e; padding: 20px; text-align: center;">无交易信号</div>
      </n-card>
    </template>

    <div v-else-if="!running" style="text-align: center; padding: 40px; color: #8b949e;">
      输入股票代码和日期范围，开始回测
    </div>
  </div>
</template>

<script setup lang="ts">
import { h, reactive, ref, computed, nextTick } from 'vue'
import {
  NCard, NInput, NDatePicker, NInputNumber, NButton,
  NSpace, NGrid, NGi, NDataTable, NAlert,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import * as echarts from 'echarts'
import { runBacktest, type BacktestResult } from '../api'

const cardStyle = {
  background: '#161b22',
  borderRadius: '12px',
  border: '1px solid #30363d',
}

const form = reactive({
  code: '600519',
  startDate: '2024-01-01',
  endDate: '2025-12-31',
  threshold: 60,
})

const running = ref(false)
const result = ref<BacktestResult | null>(null)
const errorMsg = ref('')
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const tradeSignals = computed(() => {
  if (!result.value) return []
  return result.value.daily_signals.filter((s) => s.action !== 'hold')
})

const signalColumns: DataTableColumns<any> = [
  { title: '日期', key: 'date', width: 120 },
  { title: '评分', key: 'score', width: 80 },
  {
    title: '操作', key: 'action', width: 80,
    render: (row) => h('span', {
      style: { color: row.action === 'buy' ? '#e74c3c' : '#2ecc71', fontWeight: 600 },
    }, row.action === 'buy' ? '买入' : '卖出'),
  },
  { title: '价格', key: 'price', width: 100 },
]

function renderChart() {
  if (!result.value || !chartRef.value) return
  const eq = result.value.equity_curve
  if (!eq.length) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const dates = eq.map((e) => e.date)
  const values = eq.map((e) => e.value)

  chartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: dates, axisLabel: { color: '#8b949e', fontSize: 10 } },
    yAxis: { type: 'value', axisLabel: { color: '#8b949e' }, splitLine: { lineStyle: { color: '#21262d' } } },
    series: [{
      name: '权益',
      type: 'line',
      data: values,
      smooth: false,
      lineStyle: { color: '#f0b90b', width: 1.5 },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(240, 185, 11, 0.3)' },
        { offset: 1, color: 'rgba(240, 185, 11, 0.05)' },
      ]) },
      showSymbol: false,
      markLine: {
        silent: true,
        data: [{ yAxis: 100000, label: { formatter: '初始', color: '#8b949e' } }],
        lineStyle: { color: '#484f58', type: 'dashed' },
      },
    }],
  })
}

async function handleRun() {
  if (!form.code || !form.startDate || !form.endDate) return
  running.value = true
  errorMsg.value = ''
  result.value = null

  try {
    result.value = await runBacktest({
      stock_code: form.code,
      start_date: form.startDate,
      end_date: form.endDate,
      threshold: form.threshold,
    })
    await nextTick()
    renderChart()
  } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.message || '回测失败'
    errorMsg.value = msg
  } finally {
    running.value = false
  }
}
</script>
