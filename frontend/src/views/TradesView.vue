<!-- views/TradesView.vue -->
<template>
  <div>
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-semibold text-gray-900">История сделок</h1>

      <!-- Фильтры -->
      <div class="flex gap-4">
        <div class="relative">
          <select
            v-model="selectedStrategy"
            class="block w-48 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            :disabled="isLoading"
          >
            <option value="">Все стратегии</option>
            <option v-for="strategy in strategies" :key="strategy.id" :value="strategy.id">
              {{ strategy.name }}
            </option>
          </select>
        </div>

        <div class="relative">
          <select
            v-model="selectedStatus"
            class="block w-36 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            :disabled="isLoading"
          >
            <option value="">Все статусы</option>
            <option value="OPEN">Открытые</option>
            <option value="CLOSED">Закрытые</option>
          </select>
        </div>
      </div>
    </div>

    <LoadingSpinner v-if="isLoading" text="Загрузка сделок..." />

    <ErrorState
      v-else-if="error"
      title="Ошибка загрузки сделок"
      :message="error"
      @retry="fetchData"
    />

    <template v-else>
      <!-- Статистика -->
      <div class="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div class="bg-white px-4 py-5 shadow rounded-lg sm:p-6">
          <dt class="text-sm font-medium text-gray-500">Всего сделок</dt>
          <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ tradeStats.totalTrades }}</dd>
        </div>
        <div class="bg-white px-4 py-5 shadow rounded-lg sm:p-6">
          <dt class="text-sm font-medium text-gray-500">Общий P&L</dt>
          <dd class="mt-1 text-3xl font-semibold" :class="tradeStats.totalPnl >= 0 ? 'text-green-600' : 'text-red-600'">
            {{ formatMoney(tradeStats.totalPnl) }}
          </dd>
        </div>
        <div class="bg-white px-4 py-5 shadow rounded-lg sm:p-6">
          <dt class="text-sm font-medium text-gray-500">Процент успешных</dt>
          <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ formatPercent(tradeStats.winRate) }}</dd>
        </div>
      </div>

      <!-- Пустое состояние -->
      <div v-if="filteredTrades.length === 0" class="text-center py-12 bg-white mt-8 rounded-lg shadow">
        <InboxIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">Нет сделок</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ trades.length === 0 ? 'У вас пока нет сделок.' : 'Нет сделок, соответствующих выбранным фильтрам.' }}
        </p>
      </div>

      <!-- Таблица сделок -->
      <div v-else class="mt-8 bg-white shadow rounded-lg">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Дата</th>
                <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Стратегия</th>
                <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Символ</th>
                <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Тип</th>
                <th class="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">Цена входа</th>
                <th class="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">Цена выхода</th>
                <th class="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">Объём</th>
                <th class="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">P&L</th>
                <th class="px-3 py-3.5 text-center text-sm font-semibold text-gray-900">Статус</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="trade in filteredTrades" :key="trade.id" @click="selectTrade(trade)" class="hover:bg-gray-50 cursor-pointer">
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900">
                  {{ formatDate(trade.createdAt) }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  {{ getStrategyName(trade.strategyId) }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ trade.symbol }}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  <span :class="trade.type === 'BUY' ? 'text-green-600' : 'text-red-600'">
                    {{ trade.type }}
                  </span>
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-right text-gray-500">
                  {{ formatPrice(trade.entryPrice) }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-right text-gray-500">
                  {{ trade.exitPrice ? formatPrice(trade.exitPrice) : '-' }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-right text-gray-500">
                  {{ formatQuantity(trade.quantity) }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-right">
                  <span :class="(trade.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatMoney(trade.pnl) }}
                  </span>
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-center">
                  <span
                    :class="[
                      trade.status === 'OPEN' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800',
                      'inline-flex rounded-full px-2 py-1 text-xs font-semibold'
                    ]"
                  >
                    {{ trade.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Пагинация -->
        <div v-if="totalPages > 1" class="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
          <div class="flex flex-1 justify-between sm:hidden">
            <button
              :disabled="currentPage === 1"
              @click="currentPage--"
              class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Назад
            </button>
            <button
              :disabled="currentPage === totalPages"
              @click="currentPage++"
              class="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Вперед
            </button>
          </div>
          <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Показано <span class="font-medium">{{ paginationStart }}</span> -
                <span class="font-medium">{{ paginationEnd }}</span> из
                <span class="font-medium">{{ totalTrades }}</span> сделок
              </p>
            </div>
            <div>
              <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                <button
                  v-for="page in displayedPages"
                  :key="page"
                  @click="currentPage = page"
                  :class="[
                    page === currentPage ? 'bg-primary-600 text-white' : 'bg-white text-gray-900',
                    'relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
                  ]"
                >
                  {{ page }}
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Модальное окно с деталями сделки -->
    <TradeDetailsModal
      v-if="selectedTrade"
      :trade="selectedTrade"
      @close="selectedTrade = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { InboxIcon } from '@heroicons/vue/24/outline'
import { useTradingStore } from '@/stores/trading'
import type { Trade, Strategy } from '@/types/trading'
import TradeDetailsModal from '@/components/trade/TradeDetailsModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import { formatDate, formatMoney, formatPrice, formatQuantity, formatPercent } from '@/utils/formatters'

const tradingStore = useTradingStore()
const selectedStrategy = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const itemsPerPage = 10
const selectedTrade = ref<Trade | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

const strategies = computed(() => tradingStore.strategies || [])
const trades = computed(() => tradingStore.trades || [])

const filteredTrades = computed(() => {
  let filtered = trades.value

  if (selectedStrategy.value) {
    filtered = filtered.filter(t => t.strategyId === parseInt(selectedStrategy.value))
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(t => t.status === selectedStatus.value)
  }

  const start = (currentPage.value - 1) * itemsPerPage
  return filtered.slice(start, start + itemsPerPage)
})

const tradeStats = computed(() => ({
  totalTrades: trades.value.length,
  totalPnl: trades.value.reduce((sum, trade) => sum + (trade.pnl || 0), 0),
  winRate: trades.value.length > 0
    ? (trades.value.filter(t => (t.pnl || 0) > 0).length / trades.value.length) * 100
    : 0
}))

const totalTrades = computed(() => trades.value.length)
const totalPages = computed(() => Math.ceil(totalTrades.value / itemsPerPage))
const paginationStart = computed(() => (currentPage.value - 1) * itemsPerPage + 1)
const paginationEnd = computed(() => Math.min(currentPage.value * itemsPerPage, totalTrades.value))

const displayedPages = computed(() => {
  const pages = []
  for (let i = 1; i <= totalPages.value; i++) {
    pages.push(i)
  }
  return pages
})

function getStrategyName(strategyId: number) {
  const strategy = strategies.value.find(s => s.id === strategyId)
  return strategy?.name || 'Неизвестная стратегия'
}

function selectTrade(trade: Trade) {
  selectedTrade.value = trade
}

async function fetchData() {
  isLoading.value = true
  error.value = null
  try {
    await Promise.all([
      tradingStore.fetchStrategies(),
      tradingStore.fetchTrades()
    ])
  } catch (err) {
    error.value = 'Не удалось загрузить данные. Пожалуйста, попробуйте позже.'
    console.error('Failed to fetch data:', err)
  } finally {
    isLoading.value = false
  }
}

// Reset page when filters change
watch([selectedStrategy, selectedStatus], () => {
  currentPage.value = 1
})

onMounted(() => {
  fetchData()
})
</script>