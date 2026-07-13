import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export interface LoginResponse {
  access_token: string
  token_type: string
  username: string
}

export interface UserInfo {
  id: number
  username: string
  email: string
  created_at?: string
}

export async function loginApi(username: string, password: string): Promise<LoginResponse> {
  const { data } = await http.post('/auth/login', { username, password })
  return data
}

export async function registerApi(username: string, email: string, password: string): Promise<LoginResponse> {
  const { data } = await http.post('/auth/register', { username, email, password })
  return data
}

export async function refreshTokenApi(token: string): Promise<LoginResponse> {
  const { data } = await http.post('/auth/refresh', null, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return data
}

export async function getMeApi(token: string): Promise<UserInfo> {
  const { data } = await http.get('/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
  return data
}
