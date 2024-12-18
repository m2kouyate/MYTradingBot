// stores/trading.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Strategy, Trade, Position, DashboardStats, PositionChange } from '@/types/trading'
import axios from 'axios'
import { apiClient } from '@/services/api'
import { API_ENDPOINTS } from '@/constants/api'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

export const useTradingStore = defineStore('trading', () => {
  // State
  const balanceHistory = ref<Array<{ time: string; value: number }>>([])
  const pnlHistory = ref<Array<{ time: string; value: number }>>([])
  const strategies = ref<Strategy[]>([])
  const trades = ref<Trade[]>([])
  const positions = ref<Position[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeStrategies = computed(() =>
    strategies.value.filter(s => s.isActive)
  )

  const totalBalance = computed(() =>
    positions.value.reduce((sum, pos) => sum + pos.quantity * pos.currentPrice, 0)
  )

  const dashboardStats = computed<DashboardStats>(() => ({
    totalBalance: totalBalance.value,
    activePositions: positions.value.length,
    todayPnl: positions.value.reduce((sum, pos) => sum + pos.unrealizedPnl, 0),
    winRate: calculateWinRate(trades.value)
  }))

  // Actions
  async function fetchStrategies() {
    try {
      isLoading.value = true
      const response = await apiClient.get<ApiResponse<Strategy[]>>(API_ENDPOINTS.STRATEGIES.LIST)
      strategies.value = response.data || []
    } catch (e) {
      const errorMsg = 'Failed to fetch strategies'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error('API Error (strategies):', e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPositions() {
    try {
      isLoading.value = true
      const response = await apiClient.get<ApiResponse<Position[]>>(API_ENDPOINTS.POSITIONS.LIST)
      positions.value = response.data || []
    } catch (e) {
      const errorMsg = 'Failed to fetch positions'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error('API Error (positions):', e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPositionHistory(positionId: number) {
    try {
      const response = await apiClient.get<ApiResponse<Array<{ time: string; price: number }>>>(
        API_ENDPOINTS.POSITIONS.HISTORY(positionId)
      )
      return response.data
    } catch (e) {
      const errorMsg = 'Failed to fetch position history'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error(e)
      return []
    }
  }

  async function fetchPositionChanges(positionId: number) {
    try {
      const response = await apiClient.get<ApiResponse<PositionChange[]>>(
        API_ENDPOINTS.POSITIONS.CHANGES(positionId)
      )
      return response.data
    } catch (e) {
      const errorMsg = 'Failed to fetch position changes'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error(e)
      return []
    }
  }

  async function closePosition(positionId: number) {
    try {
      await apiClient.post<ApiResponse<void>>(API_ENDPOINTS.POSITIONS.CLOSE(positionId))
      const index = positions.value.findIndex(p => p.id === positionId)
      if (index !== -1) {
        positions.value.splice(index, 1)
      }
    } catch (e) {
      const errorMsg = 'Failed to close position'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error(e)
    }
  }

  async function fetchTrades() {
    try {
      isLoading.value = true
      const response = await apiClient.get<ApiResponse<Trade[]>>(API_ENDPOINTS.TRADES.LIST)
      trades.value = response.data || []
    } catch (e) {
      const errorMsg = 'Failed to fetch trades'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error('API Error (trades):', e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTradeHistory(tradeId: number) {
    try {
      const response = await apiClient.get<ApiResponse<Array<{ time: string; price: number }>>>(
        API_ENDPOINTS.TRADES.HISTORY(tradeId)
      )
      return response.data
    } catch (e) {
      const errorMsg = 'Failed to fetch trade history'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error(e)
      return []
    }
  }

  async function createStrategy(strategy: Omit<Strategy, 'id' | 'createdAt' | 'updatedAt'>) {
    try {
      isLoading.value = true
      const response = await apiClient.post<ApiResponse<Strategy>>(API_ENDPOINTS.STRATEGIES.LIST, strategy)
      strategies.value.push(response.data)
    } catch (e) {
      const errorMsg = 'Failed to create strategy'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function updateStrategy(strategy: Strategy) {
    try {
      isLoading.value = true
      await apiClient.put<ApiResponse<Strategy>>(API_ENDPOINTS.STRATEGIES.DETAIL(strategy.id), strategy)
      const index = strategies.value.findIndex(s => s.id === strategy.id)
      if (index !== -1) {
        strategies.value[index] = strategy
      }
    } catch (e) {
      const errorMsg = 'Failed to update strategy'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  function calculateWinRate(trades: Trade[]): number {
    const closedTrades = trades.filter((t) => t.status === 'CLOSED')
    if (closedTrades.length === 0) return 0
    const winningTrades = closedTrades.filter((t) => (t.pnl || 0) > 0)
    return (winningTrades.length / closedTrades.length) * 100
  }

  async function fetchBalanceHistory(period: string = 'day') {  // добавляем параметр
    try {
      isLoading.value = true
      const response = await apiClient.get<ApiResponse<{ time: string; value: number }[]>>(
        `${API_ENDPOINTS.STRATEGIES.BALANCE_HISTORY}?period=${period}`
      )
      balanceHistory.value = response.data || []
    } catch (e) {
      const errorMsg = 'Failed to fetch balance history'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error('API Error (balance-history):', e)
      balanceHistory.value = [] // Очищаем при ошибке
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPnLHistory(period: string = 'day') {
    try {
      isLoading.value = true
      const response = await apiClient.get<ApiResponse<{ time: string; value: number }[]>>(
        `${API_ENDPOINTS.STRATEGIES.PNL_HISTORY}?period=${period}`
      )
      pnlHistory.value = response.data || [] // Проверяем, что данные пришли
    } catch (e) {
      const errorMsg = 'Failed to fetch PnL history'
      error.value = errorMsg
      notificationStore.showError(errorMsg)
      console.error('API Error (pnl-history):', e)
      pnlHistory.value = [] // Очищаем в случае ошибки
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    balanceHistory,
    pnlHistory,
    strategies,
    trades,
    positions,
    isLoading,
    error,
    // Getters
    activeStrategies,
    totalBalance,
    dashboardStats,
    // Actions
    fetchStrategies,
    fetchPositions,
    fetchPositionHistory,
    fetchPositionChanges,
    closePosition,
    fetchTrades,
    fetchTradeHistory,
    createStrategy,
    updateStrategy,
    fetchBalanceHistory,
    fetchPnLHistory
  }
})