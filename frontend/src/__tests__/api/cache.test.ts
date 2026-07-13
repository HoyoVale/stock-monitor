import { describe, it, expect, vi, beforeEach } from 'vitest'
import { cachedRequest, clearCache, invalidateAll } from '../../api/cache'

describe('cachedRequest', () => {
  beforeEach(() => {
    clearCache()
  })

  it('should call fn and cache result on first request', async () => {
    const fn = vi.fn().mockResolvedValue({ value: 42 })
    const result = await cachedRequest(fn, 'test-key', 5000)
    expect(result).toEqual({ value: 42 })
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('should return cached result within TTL', async () => {
    const fn = vi.fn().mockResolvedValue({ value: 1 })
    await cachedRequest(fn, 'key-2', 5000)
    const result = await cachedRequest(fn, 'key-2', 5000)
    expect(result).toEqual({ value: 1 })
    expect(fn).toHaveBeenCalledTimes(1) // 第二次从缓存返回
  })

  it('should re-fetch after TTL expires', async () => {
    const fn = vi.fn()
      .mockResolvedValueOnce({ value: 1 })
      .mockResolvedValueOnce({ value: 2 })

    await cachedRequest(fn, 'key-3', 0) // TTL=0 立即过期
    const result = await cachedRequest(fn, 'key-3', 0)
    expect(result).toEqual({ value: 2 })
    expect(fn).toHaveBeenCalledTimes(2)
  })

  it('should deduplicate in-flight requests', async () => {
    const fn = vi.fn().mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ value: 99 }), 50))
    )

    const [r1, r2] = await Promise.all([
      cachedRequest(fn, 'dedup', 5000),
      cachedRequest(fn, 'dedup', 5000),
    ])

    expect(r1).toEqual({ value: 99 })
    expect(r2).toEqual({ value: 99 })
    expect(fn).toHaveBeenCalledTimes(1) // 去重成功
  })

  it('different keys should not share cache', async () => {
    const fn1 = vi.fn().mockResolvedValue('a')
    const fn2 = vi.fn().mockResolvedValue('b')

    const r1 = await cachedRequest(fn1, 'k-a', 5000)
    const r2 = await cachedRequest(fn2, 'k-b', 5000)

    expect(r1).toBe('a')
    expect(r2).toBe('b')
    expect(fn1).toHaveBeenCalledTimes(1)
    expect(fn2).toHaveBeenCalledTimes(1)
  })

  it('clearCache should remove specific key', async () => {
    const fn = vi.fn()
      .mockResolvedValueOnce(1)
      .mockResolvedValueOnce(2)

    await cachedRequest(fn, 'clear-me', 10000)
    clearCache('clear-me')
    const result = await cachedRequest(fn, 'clear-me', 10000)
    expect(result).toBe(2)
    expect(fn).toHaveBeenCalledTimes(2)
  })

  it('invalidateAll should clear everything', async () => {
    const fn = vi.fn()
      .mockResolvedValueOnce(1)
      .mockResolvedValueOnce(2)

    await cachedRequest(fn, 'k1', 10000)
    invalidateAll()
    const result = await cachedRequest(fn, 'k1', 10000)
    expect(result).toBe(2)
    expect(fn).toHaveBeenCalledTimes(2)
  })
})
