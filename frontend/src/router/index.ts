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
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
