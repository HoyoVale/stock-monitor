import axios from 'axios'
import type { IndexData, QuoteData, BarData, StockInfo, WatchlistItem, AlertRule, AlertRecord } from '../types/stock'
import { cachedRequest } from './cache'

const http = axios.create({ baseURL: '/api' })

export interface MarketStatus {
  is_trading: boolean
  recommended_interval: number
  server_time: string
}

export interface BacktestResult {
  stock_code: string
  start_date: string
  end_date: string
  total_return: number
  annualized_return: number
  win_rate: number
  max_drawdown: number
  sharpe_ratio: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  equity_curve: { date: string; value: number }[]
  daily_signals: { date: string; score: number; action: string; price: number }[]
}

export async function fetchIndices(): Promise<IndexData[]> {
  return cachedRequest(
    () => http.get('/indices').then(({ data }) => data),
    'indices',
    5000,
  )
}

export async function fetchIndexBars(code: string, period = '1y'): Promise<BarData[]> {
  return cachedRequest(
    () => http.get(`/indices/${code}/bars`, { params: { period } }).then(({ data }) => data),
    `index-bars:${code}:${period}`,
    60000,
  )
}

export async function fetchStocks(search?: string): Promise<StockInfo[]> {
  return http.get('/stocks', { params: { search } }).then(({ data }) => data)
}

export async function fetchStockQuote(code: string): Promise<QuoteData> {
  return cachedRequest(
    () => http.get(`/stocks/${code}/quotes`).then(({ data }) => data),
    `quote:${code}`,
    5000,
  )
}

export async function fetchStockBars(code: string, start?: string, end?: string): Promise<BarData[]> {
  return cachedRequest(
    () => http.get(`/stocks/${code}/bars`, { params: { start, end } }).then(({ data }) => data),
    `bars:${code}:${start || ''}:${end || ''}`,
    60000,
  )
}

export async function fetchWatchlist(): Promise<WatchlistItem[]> {
  return http.get('/watchlist').then(({ data }) => data)
}

export async function addToWatchlist(code: string, name: string, group = '默认'): Promise<WatchlistItem> {
  const { data } = await http.post('/watchlist', { code, name, group_name: group })
  return data
}

export async function removeFromWatchlist(id: number): Promise<void> {
  await http.delete(`/watchlist/${id}`)
}

export async function fetchIndicators(code: string): Promise<any> {
  return cachedRequest(
    () => http.get(`/indicators/${code}`).then(({ data }) => data),
    `indicators:${code}`,
    300000,
  )
}

export async function fetchSuggestion(code: string, name?: string): Promise<any> {
  return http.get(`/suggestions/${code}`, { params: { name } }).then(({ data }) => data)
}

export async function fetchMarketStatus(): Promise<MarketStatus> {
  return cachedRequest(
    () => http.post('/indices/status').then(({ data }) => data),
    'market-status',
    15000,
  )
}

// Alert APIs

export async function fetchAlertRules(): Promise<AlertRule[]> {
  return http.get('/alerts/rules').then(({ data }) => data)
}

export async function createAlertRule(data: { stock_code: string; alert_type: string; threshold: number }): Promise<AlertRule> {
  return http.post('/alerts/rules', data).then(({ data: d }) => d)
}

export async function deleteAlertRule(id: number): Promise<void> {
  await http.delete(`/alerts/rules/${id}`)
}

export async function toggleAlertRule(id: number, enabled: boolean): Promise<void> {
  await http.patch(`/alerts/rules/${id}`, null, { params: { enabled } })
}

export async function fetchAlertRecords(limit = 50): Promise<AlertRecord[]> {
  return http.get('/alerts/records', { params: { limit } }).then(({ data }) => data)
}

export async function fetchUnreadAlertCount(): Promise<number> {
  return http.get('/alerts/unread-count').then(({ data }) => data.count)
}

// Backtest API

export async function runBacktest(params: {
  stock_code: string
  start_date: string
  end_date: string
  threshold?: number
}): Promise<BacktestResult> {
  return http.post('/backtest', params).then(({ data }) => data)
}
