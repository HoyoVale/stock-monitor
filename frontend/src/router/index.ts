import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Watchlist from '../views/Watchlist.vue'
import StockDetail from '../views/StockDetail.vue'

const routes = [
  { path: '/', name: 'dashboard', component: Dashboard, meta: { title: '大盘' } },
  { path: '/watchlist', name: 'watchlist', component: Watchlist, meta: { title: '自选股' } },
  { path: '/stock/:code', name: 'stock-detail', component: StockDetail, meta: { title: '个股详情' } },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
