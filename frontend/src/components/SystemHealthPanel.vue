<template>
  <div class="system-health-panel">
    <n-card title="系统状态" size="small" :bordered="false">
      <template #header-extra>
        <n-tag :type="health?.status === 'ok' ? 'success' : 'error'" size="small">
          {{ health?.status === 'ok' ? '运行中' : '异常' }}
        </n-tag>
      </template>
      <n-spin :show="loading">
        <n-descriptions v-if="health" :column="2" label-placement="left" size="small" bordered>
          <n-descriptions-item label="版本">{{ health.version || '-' }}</n-descriptions-item>
          <n-descriptions-item label="运行时间">{{ formatUptime(health.uptime_seconds) }}</n-descriptions-item>
          <n-descriptions-item label="Python">{{ health.python_version || '-' }}</n-descriptions-item>
          <n-descriptions-item label="日志级别">{{ health.log_level || '-' }}</n-descriptions-item>
        </n-descriptions>

        <n-divider v-if="health?.datasources" />

        <n-data-table
          v-if="datasourceRows.length"
          :columns="dsColumns"
          :data="datasourceRows"
          :bordered="true"
          size="small"
          style="margin-top: 12px"
        />
      </n-spin>

      <template #footer>
        <n-space justify="end">
          <n-button size="small" @click="fetchHealth" :loading="loading">刷新</n-button>
        </n-space>
      </template>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { NCard, NTag, NSpin, NDescriptions, NDescriptionsItem, NDivider, NDataTable, NButton, NSpace } from 'naive-ui'
import axios from 'axios'

interface DatasourceEntry {
  calls: number
  failures: number
  success_rate: number
  avg_ms: number
}

interface HealthResponse {
  status: string
  version?: string
  uptime_seconds?: number
  python_version?: string
  log_level?: string
  datasources?: Record<string, DatasourceEntry>
}

const health = ref<HealthResponse | null>(null)
const loading = ref(false)

const dsColumns = [
  { title: '数据源', key: 'name' },
  { title: '调用次数', key: 'calls' },
  { title: '失败', key: 'failures' },
  { title: '成功率', key: 'success_rate' },
  { title: '平均耗时(ms)', key: 'avg_ms' },
]

const datasourceRows = computed(() => {
  if (!health.value?.datasources) return []
  return Object.entries(health.value.datasources).map(([name, entry]) => ({
    name,
    calls: entry.calls,
    failures: entry.failures,
    success_rate: `${entry.success_rate}%`,
    avg_ms: entry.avg_ms,
  }))
})

function formatUptime(seconds?: number): string {
  if (!seconds) return '-'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h}h ${m}m ${s}s`
}

async function fetchHealth() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/health/detailed')
    health.value = data
  } catch {
    health.value = { status: 'error' }
  } finally {
    loading.value = false
  }
}

onMounted(fetchHealth)
</script>

<style scoped>
.system-health-panel {
  max-width: 720px;
  margin: 16px auto;
}
</style>
