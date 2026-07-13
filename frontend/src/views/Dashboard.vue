<template>
  <div>
    <h2 class="dashboard-title">
      大盘指数
      <span v-if="stockStore.isTrading" class="trading-badge trading">● 交易中</span>
      <span v-else class="trading-badge closed">○ 已收盘</span>
      <ConnectionStatus :status="stockStore.wsStatus" style="margin-left: 12px;" />
    </h2>
    <div class="index-grid">
      <MarketCard
        v-for="idx in stockStore.indices" :key="idx.code"
        :name="idx.name" :price="idx.price" :change="idx.change" :change_pct="idx.change_pct"
      />
    </div>
    <h3 class="section-title">上证指数走势</h3>
    <div class="chart-wrapper">
      <KLineChart
        :data="stockStore.indexBars"
        :period="period"
        @period-change="handlePeriodChange"
      />
    </div>
    <div class="bottom-grid">
      <n-card class="info-card" :bordered="false">
        <template #header><span class="card-header">热门板块</span></template>
        <div v-for="s in sectors" :key="s.name" class="sector-row">
          <span class="sector-name">{{ s.name }}</span>
          <span :style="{ color: s.pct >= 0 ? '#e74c3c' : '#2ecc71', fontFamily: '\"SF Mono\", monospace' }">
            {{ s.pct >= 0 ? '+' : '' }}{{ s.pct.toFixed(2) }}%
          </span>
        </div>
      </n-card>
      <n-card class="info-card" :bordered="false">
        <template #header><span class="card-header">涨跌停</span></template>
        <div class="limit-info">
          <div>涨停: <b style="color: #e74c3c;">--</b></div>
          <div>跌停: <b style="color: #2ecc71;">--</b></div>
          <div>上涨: <b style="color: #e74c3c;">--</b></div>
          <div>下跌: <b style="color: #2ecc71;">--</b></div>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { NCard } from 'naive-ui'
import MarketCard from '../components/MarketCard.vue'
import KLineChart from '../components/KLineChart.vue'
import ConnectionStatus from '../components/ConnectionStatus.vue'
import { useStockStore } from '../stores/stock'

const stockStore = useStockStore()
const period = ref('1y')

const sectors = ref([
  { name: '半导体', pct: 4.2 },
  { name: '证券', pct: 2.8 },
  { name: '白酒', pct: 1.5 },
  { name: '新能源', pct: 0.8 },
  { name: '银行', pct: -0.3 },
])

function handlePeriodChange(val: string) {
  period.value = val
  stockStore.loadIndexBars('000001', val)
}

onMounted(async () => {
  await stockStore.checkMarketStatus()
  await stockStore.loadIndices()
  await stockStore.loadIndexBars('000001')
  stockStore.startWebSocket([])
  stockStore.startPolling()
})

onUnmounted(() => {
  stockStore.stopPolling()
  stockStore.stopWebSocket()
})
</script>

<style scoped>
.dashboard-title {
  color: #e6edf3;
  margin-bottom: 20px;
  font-size: 18px;
}

.trading-badge {
  font-size: 13px;
  margin-left: 10px;
}

.trading {
  color: #e74c3c;
}

.closed {
  color: #8b949e;
}

.index-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.section-title {
  color: #e6edf3;
  margin-bottom: 12px;
  font-size: 16px;
}

.chart-wrapper {
  touch-action: pan-x pinch-zoom;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-top: 24px;
}

.info-card {
  background: #161b22 !important;
  border-radius: 12px;
  border: 1px solid #30363d;
}

.card-header {
  color: #e6edf3;
}

.sector-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #21262d;
}

.sector-name {
  color: #c9d1d9;
}

.limit-info {
  font-size: 14px;
  line-height: 2;
  color: #c9d1d9;
}

/* Tablet: 2-column grid */
@media (max-width: 1024px) {
  .index-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

/* Phone: 1-column grid */
@media (max-width: 640px) {
  .dashboard-title {
    font-size: 16px;
    margin-bottom: 12px;
  }

  .index-grid {
    grid-template-columns: 1fr;
    gap: 10px;
    margin-bottom: 16px;
  }

  .chart-wrapper {
    touch-action: pan-x pan-y pinch-zoom;
  }
}
</style>
