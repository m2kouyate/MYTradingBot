// services/exchangeKeys.ts
import { apiClient } from '@/services/api'
import { API_ENDPOINTS } from '@/constants/api'
import type { ExchangeKey, ExchangeKeyCreate, ExchangeKeyUpdate } from '@/types/api'

export const exchangeKeysService = {
  async getAll() {
    return await apiClient.get<ExchangeKey[]>(API_ENDPOINTS.EXCHANGE_KEYS.LIST)
  },

  async create(data: ExchangeKeyCreate) {
    return await apiClient.post<ExchangeKey>(API_ENDPOINTS.EXCHANGE_KEYS.CREATE, data)
  },

  async update(id: number, data: ExchangeKeyUpdate) {
    return await apiClient.put<ExchangeKey>(API_ENDPOINTS.EXCHANGE_KEYS.UPDATE(id), data)
  },

  async delete(id: number) {
    return await apiClient.delete(API_ENDPOINTS.EXCHANGE_KEYS.DELETE(id))
  },

  async verify(id: number) {
    return await apiClient.post(API_ENDPOINTS.EXCHANGE_KEYS.VERIFY(id))
  }
}