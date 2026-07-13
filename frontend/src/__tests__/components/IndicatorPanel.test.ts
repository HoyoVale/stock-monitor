import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import IndicatorPanel from '../../components/IndicatorPanel.vue'

vi.mock('../../api', () => ({
  fetchIndicators: vi.fn().mockResolvedValue({
    code: '000001',
    bars_count: 250,
    macd: {
      latest: { dif: 0.52, dea: 0.31, histogram: 0.21 },
      cross_signal: 'golden_cross',
    },
    rsi_14: { latest: 42.5, signal: 'neutral' },
    kdj: {
      latest: { k: 58.2, d: 54.1, j: 66.4 },
      cross_signal: 'golden_cross',
    },
    boll: {
      latest: { upper: 15.8, middle: 14.2, lower: 12.6 },
      signal: 'price_in_band',
    },
  }),
}))

describe('IndicatorPanel', () => {
  it('renders loading text when no indicators', () => {
    const wrapper = mount(IndicatorPanel, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true },
      },
    })
    expect(wrapper.text()).toContain('加载')
  })

  it('renders 4 indicator cards after load', async () => {
    const wrapper = mount(IndicatorPanel, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true },
      },
    })
    await new Promise(r => setTimeout(r, 50))
    await wrapper.vm.$nextTick()
    // @ts-ignore
    const cards = wrapper.vm.indicatorCards
    expect(cards).toHaveLength(4)
    expect(cards[0].key).toBe('macd')
    expect(cards[1].key).toBe('rsi')
    expect(cards[2].key).toBe('kdj')
    expect(cards[3].key).toBe('boll')
  })

  it('tagType maps buy to error, sell to success', () => {
    const wrapper = mount(IndicatorPanel, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true },
      },
    })
    expect(wrapper.vm.tagType('buy')).toBe('error')
    expect(wrapper.vm.tagType('sell')).toBe('success')
    expect(wrapper.vm.tagType('neutral')).toBe('default')
  })

  it('signalLabels maps golden_cross to 金叉', () => {
    const wrapper = mount(IndicatorPanel, {
      props: { code: '000001' },
      global: {
        stubs: { NCard: true, NTag: true },
      },
    })
    // @ts-ignore
    expect(wrapper.vm.signalLabels.golden_cross).toBe('金叉')
    // @ts-ignore
    expect(wrapper.vm.signalLabels.dead_cross).toBe('死叉')
    // @ts-ignore
    expect(wrapper.vm.signalLabels.oversold).toBe('超卖')
  })
})
