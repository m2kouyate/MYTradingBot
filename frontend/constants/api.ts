// constants/api.ts
export const API_BASE_URL = '/auth'

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: `${API_BASE_URL}/jwt/create/`,
    REFRESH: `${API_BASE_URL}/jwt/refresh/`,
    VERIFY: `${API_BASE_URL}/jwt/verify/`,
    REGISTER: `${API_BASE_URL}/users/`,
    PROFILE: `${API_BASE_URL}/users/me/`,
    SET_PASSWORD: `${API_BASE_URL}/users/set_password/`,
    RESET_PASSWORD: `${API_BASE_URL}/users/reset_password/`,
    RESET_PASSWORD_CONFIRM: `${API_BASE_URL}/users/reset_password_confirm/`,
    ACTIVATION: `${API_BASE_URL}/users/activation/`,
    RESEND_ACTIVATION: `${API_BASE_URL}/users/resend_activation/`,
  },
  STRATEGIES: {
    LIST: '/api/strategies/',
    DETAIL: (id: number) => `/api/strategies/${id}/`,
  },
  TRADES: {
    LIST: '/api/trades/',
    DETAIL: (id: number) => `/api/trades/${id}/`,
    HISTORY: (id: number) => `/api/trades/${id}/history/`,
  },
  POSITIONS: {
    LIST: '/api/positions/',
    DETAIL: (id: number) => `/api/positions/${id}/`,
    HISTORY: (id: number) => `/api/positions/${id}/history/`,
    CHANGES: (id: number) => `/api/positions/${id}/changes/`,
    CLOSE: (id: number) => `/api/positions/${id}/close/`,
  }
}