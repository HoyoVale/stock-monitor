import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAlertStore } from '../../stores/alerts'

// Mock API
vi.mock('../../api', () => ({
  fetchAlertRules: vi.fn().mockResolvedValue([
    { id: 1, stock_code: '600000', alert_type: 'price_above', threshold: 10.5, enabled: true, created_at: '2026-07-01T00:00:00' },
    { id: 2, stock_code: '000001', alert_type: 'price_below', threshold: 8.0, enabled: false, created_at: '2026-07-02T00:00:00' },
  ]),
  createAlertRule: vi.fn().mockResolvedValue({ id: 3, stock_code: '600519', alert_type: 'price_above', threshold: 1800, enabled: true, created_at: '2026-07-13T00:00:00' }),
  deleteAlertRule: vi.fn().mockResolvedValue(undefined),
  toggleAlertRule: vi.fn().mockResolvedValue(undefined),
  fetchAlertRecords: vi.fn().mockResolvedValue([
    { id: 1, rule_id: 1, stock_code: '600000', triggered_at: '2026-07-10T10:30:00', price: 10.6, message: 'triggered' },
  ]),
  fetchUnreadAlertCount: vi.fn().mockResolvedValue(3),
}))

describe('useAlertStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('loadRules populates rules', async () => {
    const store = useAlertStore()
    await store.loadRules()
    expect(store.rules).toHaveLength(2)
    expect(store.rules[0].stock_code).toBe('600000')
  })

  it('loadRecords populates records', async () => {
    const store = useAlertStore()
    await store.loadRecords()
    expect(store.records).toHaveLength(1)
  })

  it('addRule prepends to rules', async () => {
    const store = useAlertStore()
    await store.loadRules()
    await store.addRule({ stock_code: '600519', alert_type: 'price_above', threshold: 1800 })
    expect(store.rules).toHaveLength(3)
    expect(store.rules[0].stock_code).toBe('600519')
  })

  it('removeRule removes by id', async () => {
    const store = useAlertStore()
    await store.loadRules()
    await store.removeRule(1)
    expect(store.rules).toHaveLength(1)
    expect(store.rules[0].id).toBe(2)
  })

  it('toggleRule toggles enabled', async () => {
    const store = useAlertStore()
    await store.loadRules()
    await store.toggleRule(1, false)
    expect(store.rules[0].enabled).toBe(false)
  })

  it('checkUnread updates unreadCount', async () => {
    const store = useAlertStore()
    await store.checkUnread()
    expect(store.unreadCount).toBe(3)
  })
})
