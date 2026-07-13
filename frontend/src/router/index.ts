import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '大盘' },
  },
  {
    path: '/watchlist',
    name: 'watchlist',
    component: () => import('../views/Watchlist.vue'),
    meta: { title: '自选股' },
  },
  {
    path: '/stock/:code',
    name: 'stock-detail',
    component: () => import('../views/StockDetail.vue'),
    meta: { title: '个股详情' },
  },
  {
    path: '/alerts',
    name: 'alerts',
    component: () => import('../views/Alerts.vue'),
    meta: { title: '价格预警' },
  },
  {
    path: '/backtest',
    name: 'backtest',
    component: () => import('../views/Backtest.vue'),
    meta: { title: '历史回测' },
  },
  {
    path: '/predictions',
    name: 'predictions',
    component: () => import('../views/Predictions.vue'),
    meta: { title: 'AI 预测' },
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
