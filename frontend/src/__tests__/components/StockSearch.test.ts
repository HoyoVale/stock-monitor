import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import StockSearch from '../../components/StockSearch.vue'

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

vi.mock('../../api', () => ({
  fetchStocks: vi.fn().mockResolvedValue([
    { code: '000001', name: '平安银行' },
    { code: '000002', name: '万科A' },
  ]),
}))

describe('StockSearch', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders search input', () => {
    const wrapper = mount(StockSearch, {
      global: {
        stubs: { NAutoComplete: true },
      },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has 300ms debounce before searching', async () => {
    const wrapper = mount(StockSearch, {
      global: {
        stubs: { NAutoComplete: true },
      },
    })
    wrapper.vm.keyword = '000001'
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.loading).toBe(true)
    vi.advanceTimersByTime(299)
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.loading).toBe(true)
    vi.advanceTimersByTime(1)
    await new Promise(r => setTimeout(r, 10))
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.loading).toBe(false)
    expect(wrapper.vm.options).toHaveLength(2)
  })

  it('clears options when keyword is empty', async () => {
    const wrapper = mount(StockSearch, {
      global: {
        stubs: { NAutoComplete: true },
      },
    })
    wrapper.vm.keyword = ''
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.options).toEqual([])
  })

  it('handleSelect clears keyword and navigates', () => {
    const wrapper = mount(StockSearch, {
      global: {
        stubs: { NAutoComplete: true },
      },
    })
    wrapper.vm.keyword = 'test'
    wrapper.vm.options = [{ label: '000001 平安银行', value: '000001' }]
    wrapper.vm.handleSelect('000001')
    expect(wrapper.vm.keyword).toBe('')
    expect(wrapper.vm.options).toEqual([])
    expect(mockPush).toHaveBeenCalledWith({ name: 'stock-detail', params: { code: '000001' } })
  })
})
