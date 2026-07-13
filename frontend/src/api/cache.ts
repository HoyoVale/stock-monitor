/**
 * 前端 API 请求缓存模块。
 *
 * 功能:
 * - 飞行中请求去重: 相同 key 的并发请求共享一个 Promise
 * - TTL 结果缓存: 上次成功结果在 TTL 内直接返回
 */

interface CacheEntry<T> {
  data: T
  timestamp: number
}

const pending = new Map<string, Promise<any>>()
const cache = new Map<string, CacheEntry<any>>()

/**
 * 包装异步请求函数，添加去重和缓存。
 *
 * @param fn      原始异步请求函数
 * @param key     缓存键
 * @param ttlMs   缓存有效期（毫秒），默认 30000（30 秒）
 * @returns 包装后的函数
 */
export function cachedRequest<T>(
  fn: () => Promise<T>,
  key: string,
  ttlMs: number = 30000,
): Promise<T> {
  // 命中 TTL 缓存
  const entry = cache.get(key)
  if (entry && Date.now() - entry.timestamp < ttlMs) {
    return Promise.resolve(entry.data)
  }

  // 飞行中请求去重
  const pendingReq = pending.get(key)
  if (pendingReq) {
    return pendingReq
  }

  // 发起新请求
  const promise = fn()
    .then((data: T) => {
      cache.set(key, { data, timestamp: Date.now() })
      return data
    })
    .finally(() => {
      pending.delete(key)
    })

  pending.set(key, promise)
  return promise
}

/**
 * 清除指定 key 的缓存。
 */
export function clearCache(key?: string): void {
  if (key) {
    cache.delete(key)
  } else {
    cache.clear()
  }
}

/**
 * 使所有缓存失效。
 */
export function invalidateAll(): void {
  cache.clear()
  pending.clear()
}
