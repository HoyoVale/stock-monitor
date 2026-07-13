import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useStockStore } from '../../stores/stock'

vi.mock('../../api', () => ({
  fetchIndices: vi.fn().mockResolvedValue([
    { code: '000001', name: '上证指数', price: 3300, change: 10, change_pct: 0.3 },
  ]),
  fetchIndexBars: vi.fn().mockResolvedValue([
    { date: '2026-07-10', open: 3290, high: 3310, low: 3285, close: 3300, volume: 100000, amount: 5000000 },
  ]),
}))

describe('useStockStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with empty indices', () => {
    const store = useStockStore()
    expect(store.indices).toEqual([])
    expect(store.loading).toBe(false)
  })

  it('loadIndices sets loading to true during fetch', async () => {
    const store = useStockStore()
    const promise = store.loadIndices()
    expect(store.loading).toBe(true)
    await promise
    expect(store.loading).toBe(false)
  })

  it('loadIndices populates indices array', async () => {
    const store = useStockStore()
    await store.loadIndices()
    expect(store.indices).toHaveLength(1)
    expect(store.indices[0].code).toBe('000001')
    expect(store.indices[0].name).toBe('上证指数')
  })

  it('loadIndexBars populates indexBars array', async () => {
    const store = useStockStore()
    await store.loadIndexBars('000001')
    expect(store.indexBars).toHaveLength(1)
    expect(store.indexBars[0].close).toBe(3300)
  })
})
