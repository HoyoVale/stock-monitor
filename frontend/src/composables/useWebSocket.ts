import { ref, onUnmounted, type Ref } from 'vue'

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting'

export interface WebSocketOptions {
  /** Stock codes to subscribe to */
  codes?: string[]
  /** Auto-reconnect interval in ms (default 3000) */
  reconnectInterval?: number
  /** Max reconnect attempts (default 10, 0 = unlimited) */
  maxReconnect?: number
  /** Callback when quote data is received */
  onQuoteUpdate?: (data: any[]) => void
  /** Callback when index data is received */
  onIndexUpdate?: (data: any[]) => void
  /** Callback when connection count changes */
  onConnCount?: (count: number) => void
  /** Callback when WebSocket status changes */
  onStatusChange?: (status: ConnectionStatus) => void
}

const TOKEN_KEY = 'stock-monitor-token'

export function useWebSocket(options: WebSocketOptions = {}) {
  const {
    codes = [],
    reconnectInterval = 3000,
    maxReconnect = 10,
    onQuoteUpdate,
    onIndexUpdate,
    onConnCount,
    onStatusChange,
  } = options

  const status: Ref<ConnectionStatus> = ref('disconnected')
  const lastMessage = ref<any>(null)
  const error = ref<string | null>(null)
  const connCount = ref(0)

  let ws: WebSocket | null = null
  let reconnectCount = 0
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null
  let _statusTimer: ReturnType<typeof setInterval> | null = null

  function _buildUrl(newCodes?: string[]): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const codeList = newCodes || codes
    const codeParam = codeList.length > 0 ? `&codes=${codeList.join(',')}` : ''
    // Pass JWT token as query param for authentication
    const token = localStorage.getItem(TOKEN_KEY)
    const tokenParam = token ? `token=${encodeURIComponent(token)}` : ''
    return `${protocol}//${host}/ws/quotes?${tokenParam}${codeParam}`
  }

  function _setStatus(newStatus: ConnectionStatus) {
    status.value = newStatus
    onStatusChange?.(newStatus)
  }

  function connect(newCodes?: string[]) {
    if (ws?.readyState === WebSocket.OPEN || ws?.readyState === WebSocket.CONNECTING) {
      return
    }

    // Check if we have a token
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      _setStatus('disconnected')
      error.value = 'No auth token available'
      return
    }

    if (reconnectCount > 0 && reconnectCount <= (maxReconnect || Infinity)) {
      _setStatus('reconnecting')
    } else {
      _setStatus('connecting')
    }
    error.value = null

    try {
      ws = new WebSocket(_buildUrl(newCodes))
    } catch (e) {
      _setStatus('disconnected')
      error.value = `WebSocket connection failed: ${e}`
      scheduleReconnect()
      return
    }

    ws.onopen = () => {
      _setStatus('connected')
      reconnectCount = 0
      startHeartbeat()
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        lastMessage.value = msg

        switch (msg.type) {
          case 'quote_update':
            onQuoteUpdate?.(msg.data)
            break
          case 'index_update':
            onIndexUpdate?.(msg.data)
            break
          case 'conn_count':
            connCount.value = msg.count
            onConnCount?.(msg.count)
            break
          case 'connected':
          case 'subscribed':
          case 'pong':
          case 'heartbeat':
            break
          case 'error':
            error.value = msg.message
            // Auth error (4008) → clear token, don't reconnect
            if (msg.code === 4008) {
              localStorage.removeItem(TOKEN_KEY)
              disconnect()
            }
            break
        }
      } catch {
        // Ignore malformed messages
      }
    }

    ws.onclose = (event) => {
      _setStatus('disconnected')
      stopHeartbeat()
      // Auth errors (4008) -> don't reconnect
      if (event.code === 4008) {
        return
      }
      // Max connections (4009) -> try reconnect with backoff
      if (event.code !== 1000 && event.code !== 1001) {
        scheduleReconnect()
      }
    }

    ws.onerror = () => {
      error.value = 'WebSocket connection error'
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    stopHeartbeat()
    if (_statusTimer) {
      clearInterval(_statusTimer)
      _statusTimer = null
    }
    if (ws) {
      ws.close(1000)
      ws = null
    }
    _setStatus('disconnected')
  }

  function scheduleReconnect() {
    if (maxReconnect && reconnectCount >= maxReconnect) {
      _setStatus('disconnected')
      return
    }
    reconnectCount++
    reconnectTimer = setTimeout(() => {
      connect()
    }, reconnectInterval)
  }

  function startHeartbeat() {
    stopHeartbeat()
    heartbeatTimer = setInterval(() => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 25000)
  }

  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  function updateSubscription(newCodes: string[]) {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'subscribe', codes: newCodes }))
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    status,
    lastMessage,
    error,
    connCount,
    connect,
    disconnect,
    updateSubscription,
  }
}
