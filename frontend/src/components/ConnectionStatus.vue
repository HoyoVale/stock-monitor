<template>
  <span class="connection-indicator" :class="statusClass">
    <span class="dot"></span>
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ConnectionStatus as Status } from '../composables/useWebSocket'

const props = defineProps<{
  status: Status
}>()

const statusClass = computed(() => `status-${props.status}`)

const label = computed(() => {
  switch (props.status) {
    case 'connected': return '实时'
    case 'connecting': return '连接中...'
    case 'reconnecting': return '重连中...'
    case 'disconnected': return '离线'
    default: return '未知'
  }
})
</script>

<style scoped>
.connection-indicator {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
}
.status-connected {
  color: #2ecc71;
  background: rgba(46, 204, 113, 0.1);
}
.status-connected .dot {
  background: #2ecc71;
}
.status-connecting,
.status-reconnecting {
  color: #f39c12;
  background: rgba(243, 156, 18, 0.1);
}
.status-connecting .dot,
.status-reconnecting .dot {
  background: #f39c12;
  animation: pulse 0.8s infinite;
}
.status-disconnected {
  color: #8b949e;
  background: rgba(139, 148, 158, 0.1);
}
.status-disconnected .dot {
  background: #8b949e;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
