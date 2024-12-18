<!-- views/DashboardView.vue -->
<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900">Dashboard</h1>

    <!-- Статистика -->
    <div class="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        v-for="stat in stats"
        :key="stat.name"
        :is-loading="isLoading"
        :title="stat.name"
        :value="stat.value"
        :value-class="stat.class"
      />
    </div>

    <!-- Графики -->
    <div class="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
      <DashboardChart
        title="Баланс"
        :is-loading="isLoading"
        :data="balanceHistory"
        :value-formatter="formatMoney"
        @period-change="handleBalancePeriodChange"
      />
      <DashboardChart
        title="P&L"
        :is-loading="isLoading"
        :data="pnlHistory"
        :value-formatter="formatMoney"
        @period-change="handlePnLPeriodChange"
      />
    </div>

    <!-- Активные стратегии -->
    <div class="mt-8">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Активные стратегии</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <template v-if="isLoading">
          <SkeletonLoader
            v-for="n in 3"
            :key="n"
            :width="200"
            :height="100"
          />
        </template>
        <template v-else-if="activeStrategies.length === 0">
          <div class="col-span-3 text-center py-12 text-gray-500">
            Нет активных стратегий
          </div>
        </template>
        <template v-else>
          <div
            v-for="strategy in activeStrategies"
            :key="strategy.id"
            class="bg-white rounded-lg shadow p-6"
          >
            <div class="flex justify-between items-start">
              <div>
                <h3 class="font-medium text-gray-900">{{ strategy.name }}</h3>
                <p class="text-sm text-gray-500">{{ strategy.symbol }}</p>
              </div>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Активна
              </span>
            </div>
            <div class="mt-4 grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">Take Profit</p>
                <p class="mt-1 text-sm font-medium text-gray-900">{{ strategy.takeProfit }}%</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Stop Loss</p>
                <p class="mt-1 text-sm font-medium text-gray-900">{{ strategy.stopLoss }}%</p>
              </div>
            </div>
            <div class="mt-4">
              <p class="text-sm text-gray-500">Сделок сегодня</p>
              <p class="mt-1 text-lg font-medium text-gray-900">{{ getStrategyTodayTrades(strategy.id) }}</p>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Ошибка -->
    <div v-if="error" class="mt-4 p-4 rounded-md bg-red-50 text-red-700">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useTradingStore } from '@/stores/trading'
import StatCard from '@/components/dashboard/StatCard.vue'
import DashboardChart from '@/components/dashboard/DashboardChart.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import { formatMoney, formatPercent } from '@/utils/formatters'

const tradingStore = useTradingStore()
const isLoading = ref(false)
const error = ref<string | null>(null)
const updateInterval = ref<number | null>(null)
const isUnmounted = ref(false)

const stats = computed(() => [
  {
    name: 'Общий баланс',
    value: formatMoney(tradingStore.totalBalance),
    class: 'text-gray-900'
  },
  {
    name: 'Активные позиции',
    value: tradingStore.positions?.length || 0,
    class: 'text-gray-900'
  },
  {
    name: 'P&L сегодня',
    value: formatMoney(tradingStore.dashboardStats.todayPnl),
    class: tradingStore.dashboardStats.todayPnl >= 0 ? 'text-green-600' : 'text-red-600'
  },
  {
    name: 'Процент успешных сделок',
    value: formatPercent(tradingStore.dashboardStats.winRate),
    class: 'text-gray-900'
  }
])

const activeStrategies = computed(() =>
  tradingStore.strategies?.filter(strategy => strategy.isActive) || []
)

const balanceHistory = ref<Array<{ time: string; value: number }>>([])
const pnlHistory = ref<Array<{ time: string; value: number }>>([])

function startUpdates() {
  updateInterval.value = window.setInterval(async () => {
    if (!isUnmounted.value) {
      try {
        await Promise.all([
          tradingStore.fetchPositions(),
          tradingStore.fetchTrades()
        ])
      } catch (err) {
        console.error('Failed to update dashboard data:', err)
      }
    }
  }, 30000)
}

function getStrategyTodayTrades(strategyId: number) {
  const today = new Date()
  return tradingStore.trades.filter(trade =>
    trade.strategyId === strategyId &&
    new Date(trade.createdAt).toDateString() === today.toDateString()
  ).length
}

async function fetchData() {
  if (isUnmounted.value) return

  isLoading.value = true
  error.value = null

  try {
    await Promise.all([
      tradingStore.fetchPositions(),
      tradingStore.fetchTrades(),
      tradingStore.fetchBalanceHistory('day'),
      tradingStore.fetchPnLHistory('day')
    ])

    balanceHistory.value = tradingStore.balanceHistory
    pnlHistory.value = tradingStore.pnlHistory
    startUpdates()
  } catch (err) {
    error.value = 'Не удалось загрузить данные. Пожалуйста, попробуйте позже.'
    console.error('Failed to fetch dashboard data:', err)
  } finally {
    if (!isUnmounted.value) {
      isLoading.value = false
    }
  }
}

async function handleBalancePeriodChange(period: string) {
  try {
    isLoading.value = true
    await tradingStore.fetchBalanceHistory(period)
    balanceHistory.value = tradingStore.balanceHistory
  } catch (err) {
    console.error('Failed to fetch balance history:', err)
  } finally {
    isLoading.value = false
  }
}

async function handlePnLPeriodChange(period: string) {
  try {
    isLoading.value = true
    await tradingStore.fetchPnLHistory(period)
    pnlHistory.value = tradingStore.pnlHistory
  } catch (err) {
    console.error('Failed to fetch PnL history:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchData()
})

onBeforeUnmount(() => {
  isUnmounted.value = true
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
  }
})
</script>