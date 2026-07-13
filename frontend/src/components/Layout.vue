<template>
  <n-layout position="absolute" class="app-layout">
    <n-layout-header class="app-header">
      <div class="header-left">
        <n-button
          quaternary
          circle
          size="small"
          class="hamburger-btn"
          @click="mobileMenuOpen = !mobileMenuOpen"
          :style="{ color: '#f0b90b' }"
        >
          <template #icon><n-icon :size="22"><MenuOutline v-if="!mobileMenuOpen" /><CloseOutline v-else /></n-icon></template>
        </n-button>
        <span class="app-title">📈 股市监控系统</span>
        <StockSearch class="header-search" />
      </div>
      <div class="header-right">
        <span v-if="indices.length > 0" class="index-ticker">
          <span>上证 <b :style="{ color: indices[0]?.change >= 0 ? '#e74c3c' : '#2ecc71' }">{{ indices[0]?.price?.toFixed(0) }} {{ indices[0]?.change >= 0 ? '▲' : '▼' }}</b></span>
          <span style="margin-left: 12px;">深证 <b :style="{ color: indices[1]?.change >= 0 ? '#e74c3c' : '#2ecc71' }">{{ indices[1]?.price?.toFixed(0) }} {{ indices[1]?.change >= 0 ? '▲' : '▼' }}</b></span>
        </span>
        <n-badge :value="alertStore.unreadCount" :max="99" :show="alertStore.unreadCount > 0">
          <n-button quaternary circle size="small" @click="handleBellClick" style="color: #f0b90b;">
            <template #icon><n-icon :size="20"><NotificationsOutline /></n-icon></template>
          </n-button>
        </n-badge>
        <span class="header-time">{{ now }}</span>
      </div>
    </n-layout-header>

    <!-- Mobile overlay backdrop -->
    <div v-if="mobileMenuOpen" class="mobile-overlay" @click="mobileMenuOpen = false" />

    <n-layout has-sider position="absolute" class="layout-body">
      <n-layout-sider
        :width="220"
        :collapsed-width="64"
        show-trigger="bar"
        class="app-sider"
        :class="{ 'sider-mobile-open': mobileMenuOpen }"
      >
        <n-menu
          :value="activeKey"
          :collapsed-width="64"
          :collapsed-icon-size="22"
          :options="menuOptions"
          @update:value="handleMenuSelect"
          style="padding-top: 8px;"
        />
      </n-layout-sider>
      <n-layout-content class="app-content">
        <router-view />
      </n-layout-content>
    </n-layout>
    <n-layout-footer class="app-footer">
      数据来源: akshare &nbsp;|&nbsp; {{ now }}
    </n-layout-footer>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NLayout, NLayoutHeader, NLayoutSider, NLayoutContent, NLayoutFooter, NMenu, NButton, NBadge, NIcon } from 'naive-ui'
import { NotificationsOutline, MenuOutline, CloseOutline } from '@vicons/ionicons5'
import type { MenuOption } from 'naive-ui'
import { useStockStore } from '../stores/stock'
import { useAlertStore } from '../stores/alerts'
import StockSearch from './StockSearch.vue'

const route = useRoute()
const router = useRouter()
const stockStore = useStockStore()
const alertStore = useAlertStore()

const now = ref(new Date().toLocaleTimeString('zh-CN'))
const mobileMenuOpen = ref(false)
let timeInterval: ReturnType<typeof setInterval>
let alertInterval: ReturnType<typeof setInterval>

timeInterval = setInterval(() => { now.value = new Date().toLocaleTimeString('zh-CN') }, 1000)

const indices = computed(() => stockStore.indices)
const activeKey = computed(() => route.name as string || 'dashboard')

const menuOptions: MenuOption[] = [
  { label: '📊 大盘', key: 'dashboard' },
  { label: '⭐ 自选股', key: 'watchlist' },
  { label: '🔔 预警', key: 'alerts' },
  { label: '📈 回测', key: 'backtest' },
]

function handleMenuSelect(key: string) {
  mobileMenuOpen.value = false
  router.push({ name: key })
}

function handleBellClick() {
  router.push({ name: 'alerts' })
}

// Close mobile menu on route change
const unwatch = router.afterEach(() => {
  mobileMenuOpen.value = false
})

// Check unread alerts periodically
alertInterval = setInterval(() => {
  alertStore.checkUnread()
}, 30000)

onMounted(() => {
  stockStore.loadIndices()
  alertStore.checkUnread()
})

onUnmounted(() => {
  clearInterval(timeInterval)
  clearInterval(alertInterval)
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
  background-color: #0d1117;
}

.app-header {
  height: 56px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #30363d;
  background-color: #0d1117;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.hamburger-btn {
  display: none;
  min-width: 44px;
  min-height: 44px;
}

.app-title {
  font-size: 20px;
  font-weight: 700;
  color: #f0b90b;
}

.app-sider {
  background-color: #0d1117;
  border-right: 1px solid #30363d;
  transition: transform 0.3s ease;
}

.app-content {
  background-color: #0d1117;
  padding: 24px;
  overflow-y: auto;
}

.app-footer {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #484f58;
  border-top: 1px solid #30363d;
  background-color: #0d1117;
}

.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 90;
}

.index-ticker {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-time {
  color: #8b949e;
}

/* Tablet & Phone: show hamburger, hide desktop elements */
@media (max-width: 768px) {
  .hamburger-btn {
    display: inline-flex;
  }

  .header-search {
    display: none;
  }

  .header-time {
    display: none;
  }

  .app-title {
    font-size: 16px;
  }

  .app-header {
    padding: 0 12px;
  }

  .header-right {
    gap: 8px;
  }

  .app-sider {
    position: fixed;
    top: 56px;
    left: 0;
    bottom: 32px;
    z-index: 100;
    transform: translateX(-100%);
    box-shadow: none;
  }

  .app-sider.sider-mobile-open {
    transform: translateX(0);
    box-shadow: 4px 0 16px rgba(0, 0, 0, 0.3);
  }

  .mobile-overlay {
    display: block;
  }

  .app-content {
    padding: 12px;
  }

  .index-ticker {
    font-size: 11px;
  }

  .layout-body {
    top: 56px;
    bottom: 32px;
  }
}

/* Tablet: keep search visible but smaller */
@media (min-width: 769px) and (max-width: 1024px) {
  .header-search {
    width: 180px;
  }
}
</style>
