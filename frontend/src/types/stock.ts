export interface IndexData {
  code: string
  name: string
  price: number
  change: number
  change_pct: number
}

export interface QuoteData {
  code: string
  name: string
  price: number
  change: number
  change_pct: number
  open: number
  high: number
  low: number
  volume: number
  amount: number
}

export interface BarData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number | null
  amount: number | null
}

export interface StockInfo {
  code: string
  name: string
  exchange?: string
  industry?: string
}

export interface WatchlistItem {
  id: number
  code: string
  name: string
  added_at: string
  sort_order: number
  group_name: string
}

export interface AlertRule {
  id: number
  stock_code: string
  alert_type: 'price_above' | 'price_below'
  threshold: number
  enabled: boolean
  created_at: string
}

export interface AlertRecord {
  id: number
  rule_id: number | null
  stock_code: string
  triggered_at: string
  price: number | null
  message: string | null
}
