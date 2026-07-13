export interface UserInfo {
  id: number
  username: string
  email: string
  created_at?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  username: string
}
