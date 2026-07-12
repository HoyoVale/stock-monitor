<template>
  <n-config-provider :theme="darkTheme" :locale="zhCN" :date-locale="dateZhCN">
    <n-notification-provider>
      <n-message-provider>
        <Layout />
      </n-message-provider>
    </n-notification-provider>
  </n-config-proviler>
</template>

<script setup lang="ts">
import { darkTheme, zhCN, dateZhCN } from 'naive-ui'
import { NConfigProvider, NNotificationProvider, NMessageProvider } from 'naive-ui'
import Layout from './components/Layout.vue'
</script>

<style>
body {
  margin: 0;
  background-color: #0d1117;
  color: #e6edf3;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
#app {
  min-height: 100vh;
}
</style>
