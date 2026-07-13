import axios from 'axios'
import type { IndexData, QuoteData, BarData, StockInfo, WatchlistItem } from '../types/stock'

const http = axios.create({ baseURL: '/api' })

export async function fetchIndices(): Promise<IndexData[]> {
  const { data } = await http.get('/indices')
  return data
}

export async function fetchIndexBars(code: string, period = '1y'): Promise<BarData[]> {
  const { data } = await http.get(`/indices/${code}/bars`, { params: { period } })
  return data
}

export async function fetchStocks(search?: string): Promise<StockInfo[]> {
  const { data } = await http.get('/stocks', { params: { search } })
  return data
}

export async function fetchStockQuote(code: string): Promise<QuoteData> {
  const { data } = await http.get(`/stocks/${code}/quotes`)
  return data
}

export async function fetchStockBars(code: string, start?: string, end?: string): Promise<BarData[]> {
  const { data } = await http.get(`/stocks/${code}/bars`, { params: { start, end } })
  return data
}

export async function fetchWatchlist(): Promise<WatchlistItem[]> {
  const { data } = await http.get('/watchlist')
  return data
}

export async function addToWatchlist(code: string, name: string, group = '默认'): Promise<WatchlistItem> {
  const { data } = await http.post('/watchlist', { code, name, group_name: group })
  return data
}

export async function removeFromWatchlist(id: number): Promise<void> {
  await http.delete(`/watchlist/${id}`)
}

export async function fetchIndicators(code: string): Promise<any> {
  const { data } = await http.get(`/indicators/${code}`)
  return data
}

export async function fetchSuggestion(code: string, name?: string): Promise<any> {
  const { data } = await http.get(`/suggestions/${code}`, { params: { name } })
  return data
}
