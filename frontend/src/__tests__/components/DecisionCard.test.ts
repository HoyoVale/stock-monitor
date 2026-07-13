import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DecisionCard from '../../components/DecisionCard.vue'

vi.mock('../../api', () => ({
  fetchSuggestion: vi.fn().mockResolvedValue({
    code: '000001',
    data_source: { function: 'akshare stock_zh_a_hist', timestamp: '2026-07-13T10:00:00' },
    indicators: {
      macd: { raw_value: { dif: 0.5, dea: 0.3 }, signal: 'buy', judgment: '金叉', explanation: 'DIF上穿DEA', weight: 30 },
      rsi: { raw_value: { value: 45 }, signal: 'neutral', judgment: '中性', explanation: 'RSI在正常范围', weight: 20 },
      kdj: { raw_value: { k: 60, d: 55, j: 70 }, signal: 'buy', judgment: '金叉', explanation: 'K上穿D', weight: 20 },
      boll: { raw_value: { upper: 16, middle: 14, lower: 12 }, signal: 'neutral', judgment: '正常', explanation: '价格在布林带内', weight: 15 },
      ma_arrange: { raw_value: { sma_5: 14.5, sma_10: 14, sma_20: 13.5, sma_60: 12 }, signal: 'buy', judgment: '多头排列', explanation: '短期均线在长期上方', weight: 15 },
    },
    overall_score: 72,
    rating: 'buy',
    rating_cn: '买入',
    summary: '综合建议买入',
    risk_tips: ['注意回调风险'],
    position_suggestion: '建议半仓',
  }),
}))

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

describe('DecisionCard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders loading text when no suggestion', () => {
    const wrapper = mount(DecisionCard, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true, NModal: true, NTable: true },
      },
    })
    expect(wrapper.text()).toContain('加载')
  })

  it('renders suggestion data after mount', async () => {
    const wrapper = mount(DecisionCard, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true, NModal: true, NTable: true },
      },
    })
    await new Promise(r => setTimeout(r, 50))
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.suggestion).not.toBeNull()
  })

  it('computes correct stars for score 72', async () => {
    const wrapper = mount(DecisionCard, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true, NModal: true, NTable: true },
      },
    })
    await new Promise(r => setTimeout(r, 50))
    await wrapper.vm.$nextTick()
    // @ts-ignore
    expect(wrapper.vm.stars).toBe(4)
  })

  it('scoreColor red for buy rating (score >= 60)', async () => {
    const wrapper = mount(DecisionCard, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true, NModal: true, NTable: true },
      },
    })
    await new Promise(r => setTimeout(r, 50))
    await wrapper.vm.$nextTick()
    // @ts-ignore
    expect(wrapper.vm.scoreColor).toBe('#e74c3c')
  })

  it('ratingTagType returns error for buy/strong_buy', async () => {
    const wrapper = mount(DecisionCard, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true, NModal: true, NTable: true },
      },
    })
    await new Promise(r => setTimeout(r, 50))
    await wrapper.vm.$nextTick()
    // @ts-ignore
    expect(wrapper.vm.ratingTagType).toBe('error')
  })

  it('tagType returns error for buy signal', () => {
    const wrapper = mount(DecisionCard, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true, NModal: true, NTable: true },
      },
    })
    expect(wrapper.vm.tagType('buy')).toBe('error')
    expect(wrapper.vm.tagType('sell')).toBe('success')
    expect(wrapper.vm.tagType('neutral')).toBe('default')
    expect(wrapper.vm.tagType('unknown')).toBe('default')
  })

  it('indicatorRows parses all 5 indicators', async () => {
    const wrapper = mount(DecisionCard, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true, NModal: true, NTable: true },
      },
    })
    await new Promise(r => setTimeout(r, 50))
    await wrapper.vm.$nextTick()
    // @ts-ignore
    const rows = wrapper.vm.indicatorRows
    expect(rows).toHaveLength(5)
    expect(rows[0].weight).toBe(30)
    expect(rows[0].signal).toBe('buy')
  })
})
