import { setAccessToken } from './api-client'

const REFRESH_TOKEN_KEY = 'refresh_token'

export function storeTokens(accessToken: string, refreshToken: string) {
  setAccessToken(accessToken)
  if (typeof window !== 'undefined') {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  }
}

export function clearTokens() {
  setAccessToken(null)
  if (typeof window !== 'undefined') {
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }
}

export function getStoredRefreshToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  }
  return null
}
