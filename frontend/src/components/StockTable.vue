<template>
  <n-data-table
    :columns="columns"
    :data="data"
    :loading="loading"
    :bordered="false"
    :single-line="false"
    :style="{ background: 'transparent' }"
    size="small"
  />
</template>

<script setup lang="ts">
import { h } from 'vue'
import { NDataTable, NButton } from 'naive-ui'
import type { DataTableColumn } from 'naive-ui'
import type { QuoteData } from '../types/stock'

defineProps<{
  data: QuoteData[]
  loading?: boolean
}>()

const columns: DataTableColumn<QuoteData>[] = [
  { title: '代码', key: 'code', width: 100 },
  { title: '名称', key: 'name', width: 120 },
  {
    title: '现价', key: 'price', width: 100,
    render: r => h('span', { style: { fontFamily: '"SF Mono", monospace' } }, r.price?.toFixed(2)),
  },
  {
    title: '涨跌幅', key: 'change_pct', width: 100,
    render: r => {
      const color = r.change_pct >= 0 ? '#e74c3c' : '#2ecc71'
      return h('span', { style: { color, fontFamily: '"SF Mono", monospace', fontWeight: 700 } },
        `${r.change_pct >= 0 ? '+' : ''}${r.change_pct.toFixed(2)}%`)
    },
  },
  {
    title: '涨跌额', key: 'change', width: 100,
    render: r => h('span', { style: { color: r.change >= 0 ? '#e74c3c' : '#2ecc71', fontFamily: '"SF Mono", monospace' } },
      `${r.change >= 0 ? '+' : ''}${r.change.toFixed(2)}`),
  },
  { title: '今开', key: 'open', width: 100, render: r => h('span', { style: { fontFamily: '"SF Mono", monospace' } }, r.open?.toFixed(2)) },
  { title: '昨收', key: 'close', width: 100, render: r => h('span', { style: { fontFamily: '"SF Mono", monospace' } }, r.close?.toFixed(2)) },
]
</script>
