<template>
  <n-layout position="absolute" style="height: 100vh; background-color: #0d1117">
    <n-layout-header style="height: 56px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #30363d; background-color: #0d1117;">
      <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 20px; font-weight: 700; color: #f0b90b;">📈 股市监控系统</span>
      </div>
      <div style="display: flex; align-items: center; gap: 20px; font-size: 13px;">
        <span v-if="indices.length > 0">
          <span>上证 <b :style="{ color: indices[0]?.change >= 0 ? '#e74c3c' : '#2ecc71' }">{{ indices[0]?.price?.toFixed(0) }} {{ indices[0]?.change >= 0 ? '▲' : '▼' }}</b></span>
          <span style="margin-left: 12px;">深证 <b :style="{ color: indices[1]?.change >= 0 ? '#e74c3c' : '#2ecc71' }">{{ indices[1]?.price?.toFixed(0) }} {{ indices[1]?.change >= 0 ? '▲' : '▼' }}</b></span>
        </span>
        <span style="color: #8b949e;">{{ now }}</span>
      </div>
    </n-layout-header>
    <n-layout has-sider position="absolute" style="top: 56px; bottom: 32px;">
      <n-layout-sider :width="220" :collapsed-width="64" show-trigger="bar" style="background-color: #0d1117; border-right: 1px solid #30363d;">
        <n-menu
          :value="activeKey"
          :collapsed-width="64"
          :collapsed-icon-size="22"
          :options="menuOptions"
          @update:value="handleMenuSelect"
          style="padding-top: 8px;"
        />
      </n-layout-sider>
      <n-layout-content style="background-color: #0d1117; padding: 24px; overflow-y: auto;">
        <router-view />
      </n-layout-content>
    </n-layout>
    <n-layout-footer style="height: 32px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #484f58; border-top: 1px solid #30363d; background-color: #0d1117;">
      数据来源: akshare &nbsp;|&nbsp; {{ now }}
    </n-layout-footer>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NLayout, NLayoutHeader, NLayoutSider, NLayoutContent, NLayoutFooter, NMenu } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { useStockStore } from '../stores/stock'

const route = useRoute()
const router = useRouter()
const stockStore = useStockStore()

const now = ref(new Date().toLocaleTimeString('zh-CN'))
setInterval(() => { now.value = new Date().toLocaleTimeString('zh-CN') }, 1000)

const indices = computed(() => stockStore.indices)
const activeKey = computed(() => route.name as string || 'dashboard')

const menuOptions: MenuOption[] = [
  { label: '📊 大盘', key: 'dashboard' },
  { label: '⭐ 自选股', key: 'watchlist' },
]

function handleMenuSelect(key: string) {
  router.push({ name: key })
}

onMounted(() => {
  stockStore.loadIndices()
})
</script>
