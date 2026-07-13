import axios from 'axios'
import type { IndexData, QuoteData, BarData, StockInfo, WatchlistItem } from '../types/stock'
import { cachedRequest } from './cache'

const http = axios.create({ baseURL: '/api' })

export interface MarketStatus {
  is_trading: boolean
  recommended_interval: number
  server_time: string
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
    300000, // 指标缓存 5 分钟
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
