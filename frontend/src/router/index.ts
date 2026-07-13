import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '大盘', requiresAuth: false },
  },
  {
    path: '/watchlist',
    name: 'watchlist',
    component: () => import('../views/Watchlist.vue'),
    meta: { title: '自选股', requiresAuth: false },
  },
  {
    path: '/stock/:code',
    name: 'stock-detail',
    component: () => import('../views/StockDetail.vue'),
    meta: { title: '个股详情', requiresAuth: false },
  },
  {
    path: '/alerts',
    name: 'alerts',
    component: () => import('../views/Alerts.vue'),
    meta: { title: '价格预警', requiresAuth: true },
  },
  {
    path: '/backtest',
    name: 'backtest',
    component: () => import('../views/Backtest.vue'),
    meta: { title: '历史回测', requiresAuth: true },
  },
  {
    path: '/predictions',
    name: 'predictions',
    component: () => import('../views/Predictions.vue'),
    meta: { title: 'AI 预测', requiresAuth: true },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', requiresAuth: false },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册', requiresAuth: false },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard: redirect to login for protected routes
router.beforeEach(async (to, _from, next) => {
  const { useAuthStore } = await import('../stores/auth')
  const auth = useAuthStore()

  // Try to restore user session from stored token
  if (auth.token && !auth.user) {
    await auth.fetchUser()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
