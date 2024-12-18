// types/api.ts

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  message: string;
  code?: string;
  field?: string;
}

// Djoser auth types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
  re_password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface TokenRefreshResponse {
  access: string;
}

export interface TokenVerifyResponse {
  detail: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
}

export interface PasswordResetConfirm {
  uid: string;
  token: string;
  new_password: string;
  re_new_password: string;
}

export interface ActivationConfirm {
  uid: string;
  token: string;
}

export interface SetPassword {
  new_password: string;
  re_new_password: string;
  current_password: string;
}

export interface ExchangeKey {
  id: number
  exchange: 'BINANCE' | 'BYBIT'
  api_key: string
  api_secret: string
  testnet: boolean
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface ExchangeKeyCreate {
  exchange: string
  api_key: string
  api_secret: string
  testnet: boolean
}

export interface ExchangeKeyUpdate {
  api_key?: string
  api_secret?: string
  testnet?: boolean
  is_active?: boolean
}