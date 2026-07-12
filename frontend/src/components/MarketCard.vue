<template>
  <n-card :style="{ background: '#161b22', borderRadius: '12px', border: '1px solid #30363d' }" :bordered="false">
    <div style="text-align: center;">
      <div style="font-size: 14px; color: #8b949e; margin-bottom: 8px;">{{ name }}</div>
      <div style="font-size: 28px; font-weight: 700; font-family: 'SF Mono', 'Courier New', monospace;" :style="{ color: change >= 0 ? '#e74c3c' : '#2ecc71' }">
        {{ price.toFixed(2) }}
      </div>
      <div style="font-size: 14px; margin-top: 4px;" :style="{ color: change >= 0 ? '#e74c3c' : '#2ecc71' }">
        <template v-if="change >= 0">▲</template><template v-else>▼</template>
        {{ Math.abs(change).toFixed(2) }} ({{ change_pct >= 0 ? '+' : '' }}{{ change_pct.toFixed(2) }}%)
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { NCard } from 'naive-ui'

defineProps<{
  name: string
  price: number
  change: number
  change_pct: number
}>()
</script>
