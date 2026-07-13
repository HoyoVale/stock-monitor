<template>
  <div>
    <h2 style="color: #e6edf3; margin-bottom: 20px; font-size: 18px;">价格预警管理</h2>

    <!-- 创建预警表单 -->
    <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d', marginBottom: '20px' }" :bordered="false">
      <template #header><span style="color: #e6edf3; font-weight: 600;">新建预警规则</span></template>
      <n-space vertical :size="12">
        <n-grid :cols="4" :x-gap="12">
          <n-gi>
            <n-input v-model:value="form.code" placeholder="股票代码 (如 600000)" style="width: 100%;" />
          </n-gi>
          <n-gi>
            <n-select
              v-model:value="form.alertType"
              :options="typeOptions"
              placeholder="预警类型"
            />
          </n-gi>
          <n-gi>
            <n-input-number v-model:value="form.threshold" placeholder="触发价格" style="width: 100%;" :min="0" :step="0.01" />
          </n-gi>
          <n-gi>
            <n-button type="primary" @click="handleCreate" :loading="submitting" style="width: 100%;">创建预警</n-button>
          </n-gi>
        </n-grid>
      </n-space>
    </n-card>

    <!-- 预警规则列表 -->
    <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d', marginBottom: '20px' }" :bordered="false">
      <template #header><span style="color: #e6edf3; font-weight: 600;">预警规则 ({{ store.rules.length }})</span></template>
      <n-data-table
        v-if="store.rules.length > 0"
        :columns="ruleColumns"
        :data="store.rules"
        :bordered="false"
        size="small"
        :row-class-name="() => 'alert-row'"
      />
      <div v-else style="color: #8b949e; padding: 20px; text-align: center;">暂无预警规则，请创建</div>
    </n-card>

    <!-- 触发历史 -->
    <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false">
      <template #header><span style="color: #e6edf3; font-weight: 600;">触发历史</span></template>
      <n-data-table
        v-if="store.records.length > 0"
        :columns="recordColumns"
        :data="store.records"
        :bordered="false"
        size="small"
        :row-class-name="() => 'alert-row'"
      />
      <div v-else style="color: #8b949e; padding: 20px; text-align: center;">暂无触发记录</div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, reactive, ref, onMounted } from 'vue'
import { NCard, NInput, NSelect, NInputNumber, NButton, NSpace, NGrid, NGi, NDataTable, NSwitch, NPopconfirm } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useAlertStore } from '../stores/alerts'
import type { AlertRule, AlertRecord } from '../types/stock'

const store = useAlertStore()
const submitting = ref(false)

const form = reactive({
  code: '',
  alertType: 'price_above' as string,
  threshold: 0,
})

const typeOptions = [
  { label: '价格上穿', value: 'price_above' },
  { label: '价格下穿', value: 'price_below' },
]

const ALERT_TYPE_LABELS: Record<string, string> = {
  price_above: '上穿',
  price_below: '下穿',
}

async function handleCreate() {
  if (!form.code || form.threshold <= 0) return
  submitting.value = true
  try {
    await store.addRule({
      stock_code: form.code,
      alert_type: form.alertType,
      threshold: form.threshold,
    })
    form.code = ''
    form.threshold = 0
  } finally {
    submitting.value = false
  }
}

const ruleColumns: DataTableColumns<AlertRule> = [
  { title: '股票代码', key: 'stock_code', width: 120 },
  {
    title: '预警类型', key: 'alert_type', width: 100,
    render: (row) => ALERT_TYPE_LABELS[row.alert_type] || row.alert_type,
  },
  { title: '触发价格', key: 'threshold', width: 120 },
  {
    title: '状态', key: 'enabled', width: 80,
    render: (row) => h(NSwitch, {
      value: row.enabled,
      onUpdateValue: (v: boolean) => store.toggleRule(row.id, v),
    }),
  },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 80,
    render: (row) => h(NPopconfirm, {
      onPositiveClick: () => store.removeRule(row.id),
    }, {
      trigger: () => h(NButton, { size: 'tiny', type: 'error', quaternary: true }, { default: () => '删除' }),
      default: () => '确定删除此预警规则？',
    }),
  },
]

const recordColumns: DataTableColumns<AlertRecord> = [
  { title: '股票代码', key: 'stock_code', width: 120 },
  { title: '触发价格', key: 'price', width: 120 },
  { title: '消息', key: 'message', ellipsis: { tooltip: true } },
  { title: '触发时间', key: 'triggered_at', width: 180 },
]

onMounted(async () => {
  await Promise.all([store.loadRules(), store.loadRecords()])
})
</script>

<style>
.alert-row td {
  color: #c9d1d9 !important;
}
</style>
