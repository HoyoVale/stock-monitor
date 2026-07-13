import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../Login.vue'

describe('Login.vue', () => {
  let router: ReturnType<typeof createRouter>

  beforeEach(() => {
    setActivePinia(createPinia())
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/login', component: Login },
        { path: '/register', component: { template: '<div>Register</div>' } },
      ],
    })
  })

  it('renders the login form', async () => {
    await router.push('/login')
    await router.isReady()

    const wrapper = mount(Login, {
      global: {
        plugins: [createPinia(), router],
        stubs: { 'n-card': true, 'n-form': true, 'n-form-item': true, 'n-input': true, 'n-button': true },
      },
    })

    expect(wrapper.find('.auth-page').exists()).toBe(true)
  })

  it('has register link', async () => {
    await router.push('/login')
    await router.isReady()

    const wrapper = mount(Login, {
      global: {
        plugins: [createPinia(), router],
        stubs: { 'n-card': true, 'n-form': true, 'n-form-item': true, 'n-input': true, 'n-button': true },
      },
    })

    expect(wrapper.text()).toContain('立即注册')
  })
})
