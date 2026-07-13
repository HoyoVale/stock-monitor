import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { nextTick } from 'vue'
import { useWebSocket } from '../useWebSocket'

describe('useWebSocket', () => {
  let mockWs: any

  beforeEach(() => {
    mockWs = {
      readyState: WebSocket.CONNECTING,
      send: vi.fn(),
      close: vi.fn(),
      onopen: null as any,
      onmessage: null as any,
      onclose: null as any,
      onerror: null as any,
    }

    vi.spyOn(globalThis, 'WebSocket').mockImplementation(() => mockWs as any)
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('should initialize with disconnected status', () => {
    const { status } = useWebSocket()
    expect(status.value).toBe('disconnected')
  })

  it('should set status to connecting when connect is called', () => {
    const { status, connect } = useWebSocket()
    connect()
    expect(status.value).toBe('connecting')
  })

  it('should set status to connected on open', async () => {
    const { status, connect } = useWebSocket()
    connect()
    mockWs.onopen()
    await nextTick()
    expect(status.value).toBe('connected')
  })

  it('should call onQuoteUpdate when quote_update message received', async () => {
    const onQuoteUpdate = vi.fn()
    const { connect } = useWebSocket({ onQuoteUpdate })
    connect()
    mockWs.onmessage({ data: JSON.stringify({ type: 'quote_update', data: [{ code: '000001' }] }) })
    await nextTick()
    expect(onQuoteUpdate).toHaveBeenCalledWith([{ code: '000001' }])
  })

  it('should call onIndexUpdate when index_update message received', async () => {
    const onIndexUpdate = vi.fn()
    const { connect } = useWebSocket({ onIndexUpdate })
    connect()
    mockWs.onmessage({ data: JSON.stringify({ type: 'index_update', data: [{ code: '000001' }] }) })
    await nextTick()
    expect(onIndexUpdate).toHaveBeenCalledWith([{ code: '000001' }])
  })

  it('should send ping messages for heartbeat', () => {
    const { connect } = useWebSocket()
    connect()
    mockWs.readyState = WebSocket.OPEN
    mockWs.onopen()
    vi.advanceTimersByTime(25000)
    expect(mockWs.send).toHaveBeenCalledWith(JSON.stringify({ type: 'ping' }))
  })

  it('should resume polling fallback when WebSocket disconnected', async () => {
    const { status, connect } = useWebSocket()
    connect()
    mockWs.onclose({ code: 1006 })
    await nextTick()
    expect(status.value).toBe('disconnected')
  })

  it('should reconnect on abnormal close', async () => {
    const { connect } = useWebSocket()
    connect()
    vi.clearAllMocks()
    mockWs.onclose({ code: 1006 })
    vi.advanceTimersByTime(3000)
    expect(WebSocket).toHaveBeenCalledTimes(1) // 1 reconnect after initial
  })

  it('should NOT reconnect on normal close', async () => {
    const { connect } = useWebSocket()
    connect()
    mockWs.onclose({ code: 1000 })
    vi.advanceTimersByTime(5000)
    expect(WebSocket).toHaveBeenCalledTimes(1) // only initial
  })
})
