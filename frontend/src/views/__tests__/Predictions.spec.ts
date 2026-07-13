import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Predictions from '../Predictions.vue'

describe('Predictions.vue', () => {
  it('renders page title', () => {
    const wrapper = mount(Predictions, {
      global: {
        stubs: {
          NCard: { template: '<div><slot /><slot name="header" /></div>' },
          NInput: { template: '<input />', props: ['value'] },
          NInputNumber: { template: '<input />', props: ['value'] },
          NButton: { template: '<button><slot /></button>' },
          NSpace: { template: '<div><slot /></div>' },
          NDataTable: { template: '<table />' },
          NAlert: { template: '<div><slot /></div>' },
        },
      },
    })
    expect(wrapper.find('h2').text()).toBe('AI 股价预测')
  })

  it('shows placeholder text when no result', () => {
    const wrapper = mount(Predictions, {
      global: {
        stubs: {
          NCard: { template: '<div><slot /><slot name="header" /></div>' },
          NInput: { template: '<input />', props: ['value'] },
          NInputNumber: { template: '<input />', props: ['value'] },
          NButton: { template: '<button><slot /></button>' },
          NSpace: { template: '<div><slot /></div>' },
          NDataTable: { template: '<table />' },
          NAlert: { template: '<div><slot /></div>' },
        },
      },
    })
    expect(wrapper.html()).toContain('AI 预测结果')
  })
})
