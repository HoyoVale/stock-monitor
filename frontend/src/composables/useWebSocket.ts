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
}

export function useWebSocket(options: WebSocketOptions = {}) {
  const {
    codes = [],
    reconnectInterval = 3000,
    maxReconnect = 10,
    onQuoteUpdate,
    onIndexUpdate,
  } = options

  const status: Ref<ConnectionStatus> = ref('disconnected')
  const lastMessage = ref<any>(null)
  const error = ref<string | null>(null)

  let ws: WebSocket | null = null
  let reconnectCount = 0
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null

  const wsUrl = (() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const codeParam = codes.length > 0 ? `?codes=${codes.join(',')}` : ''
    return `${protocol}//${host}/ws/quotes${codeParam}`
  })()

  function connect(newCodes?: string[]) {
    if (ws?.readyState === WebSocket.OPEN || ws?.readyState === WebSocket.CONNECTING) {
      return
    }

    if (reconnectCount > 0 && reconnectCount <= (maxReconnect || Infinity)) {
      status.value = 'reconnecting'
    } else {
      status.value = 'connecting'
    }
    error.value = null

    try {
      const url = newCodes
        ? (() => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
            const host = window.location.host
            return `${protocol}//${host}/ws/quotes?codes=${newCodes.join(',')}`
          })()
        : wsUrl

      ws = new WebSocket(url)
    } catch (e) {
      status.value = 'disconnected'
      error.value = `WebSocket connection failed: ${e}`
      scheduleReconnect()
      return
    }

    ws.onopen = () => {
      status.value = 'connected'
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
          case 'connected':
          case 'subscribed':
          case 'pong':
          case 'heartbeat':
            // System messages, no action needed
            break
          case 'error':
            error.value = msg.message
            break
        }
      } catch {
        // Ignore malformed messages
      }
    }

    ws.onclose = (event) => {
      status.value = 'disconnected'
      stopHeartbeat()
      // Don't reconnect on normal closure or if max reconnects reached
      if (event.code !== 1000 && event.code !== 1001) {
        scheduleReconnect()
      }
    }

    ws.onerror = () => {
      // onclose will fire after onerror
      error.value = 'WebSocket connection error'
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    stopHeartbeat()
    if (ws) {
      ws.close(1000)
      ws = null
    }
    status.value = 'disconnected'
  }

  function scheduleReconnect() {
    if (maxReconnect && reconnectCount >= maxReconnect) {
      status.value = 'disconnected'
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
    connect,
    disconnect,
    updateSubscription,
  }
}
