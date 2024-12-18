<!-- views/PositionsView.vue -->
<template>
  <div>
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-semibold text-gray-900">Активные позиции</h1>

      <!-- Сводная информация -->
      <div class="flex gap-4">
        <div class="text-sm">
          <span class="text-gray-500">Всего позиций:</span>
          <span class="ml-1 font-medium">{{ positions.length }}</span>
        </div>
        <div class="text-sm">
          <span class="text-gray-500">Общий P&L:</span>
          <span
            class="ml-1 font-medium"
            :class="totalUnrealizedPnl >= 0 ? 'text-green-600' : 'text-red-600'"
          >
            {{ formatMoney(totalUnrealizedPnl) }}
          </span>
        </div>
      </div>
    </div>

    <LoadingSpinner v-if="isLoading" text="Загрузка позиций..." />

    <ErrorState
      v-else-if="error"
      title="Ошибка загрузки позиций"
      :message="error"
      @retry="fetchData"
    />

    <template v-else>
      <!-- Пустое состояние -->
      <div v-if="positions.length === 0" class="text-center py-12 bg-white mt-8 rounded-lg shadow">
        <Inbox class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">Нет активных позиций</h3>
        <p class="mt-1 text-sm text-gray-500">
          У вас пока нет открытых позиций.
        </p>
      </div>

      <!-- Карточки позиций -->
      <div v-else class="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="position in positions"
          :key="position.id"
          class="bg-white shadow rounded-lg overflow-hidden"
        >
          <div class="px-4 py-5 sm:p-6">
            <!-- Заголовок позиции -->
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-medium text-gray-900">
                  {{ position.symbol }}
                </h3>
                <p class="text-sm text-gray-500">
                  {{ getStrategyName(position.strategyId) }}
                </p>
              </div>
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getStatusClass(position.unrealizedPnl)"
              >
                {{ formatPercent(getPositionReturn(position)) }}
              </span>
            </div>

            <!-- Детали позиции -->
            <div class="mt-4 grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">Цена входа</p>
                <p class="mt-1 text-sm font-medium text-gray-900">
                  {{ formatPrice(position.entryPrice) }}
                </p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Текущая цена</p>
                <p class="mt-1 text-sm font-medium text-gray-900">
                  {{ formatPrice(position.currentPrice) }}
                </p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Количество</p>
                <p class="mt-1 text-sm font-medium text-gray-900">
                  {{ formatQuantity(position.quantity) }}
                </p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Общая стоимость</p>
                <p class="mt-1 text-sm font-medium text-gray-900">
                  {{ formatMoney(position.currentPrice * position.quantity) }}
                </p>
              </div>
            </div>

            <!-- P&L -->
            <div class="mt-4">
              <p class="text-sm text-gray-500">Нереализованный P&L</p>
              <p
                class="mt-1 text-lg font-semibold"
                :class="position.unrealizedPnl >= 0 ? 'text-green-600' : 'text-red-600'"
              >
                {{ formatMoney(position.unrealizedPnl) }}
              </p>
            </div>

            <!-- Управление позицией -->
            <div class="mt-4 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500">Stop Loss</span>
                <div class="flex items-center gap-2">
                  <input
                    type="number"
                    v-model="position.stopLoss"
                    class="block w-24 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                    step="0.01"
                  />
                  <button
                    @click="updateStopLoss(position)"
                    class="inline-flex items-center rounded bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10"
                  >
                    Обновить
                  </button>
                </div>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500">Take Profit</span>
                <div class="flex items-center gap-2">
                  <input
                    type="number"
                    v-model="position.takeProfit"
                    class="block w-24 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                    step="0.01"
                  />
                  <button
                    @click="updateTakeProfit(position)"
                    class="inline-flex items-center rounded bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10"
                  >
                    Обновить
                  </button>
                </div>
              </div>
            </div>

            <!-- Действия -->
            <div class="mt-4 flex gap-2">
              <button
                @click="showDetails(position)"
                class="flex-1 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
              >
                Детали
              </button>
              <button
                @click="closePosition(position)"
                class="flex-1 rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500"
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Модальное окно с деталями позиции -->
    <PositionDetailsModal
      v-if="selectedPosition"
      :position="selectedPosition"
      @close="selectedPosition = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Inbox } from 'lucide-vue-next'
import { useTradingStore } from '@/stores/trading'
import type { Position } from '@/types/trading'
import PositionDetailsModal from '@/components/position/PositionDetailsModal.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import { formatDate, formatMoney, formatPrice, formatQuantity, formatPercent } from '@/utils/formatters'

const tradingStore = useTradingStore()
const selectedPosition = ref<Position | null>(null)
const updateInterval = ref<number | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const isUnmounted = ref(false)

const positions = computed(() => tradingStore.positions || [])

const totalUnrealizedPnl = computed(() =>
  positions.value.reduce((sum, pos) => sum + (pos.unrealizedPnl || 0), 0)
)

function getStrategyName(strategyId: number) {
  const strategy = tradingStore.strategies.find(s => s.id === strategyId)
  return strategy?.name || 'Неизвестная стратегия'
}

function getPositionReturn(position: Position) {
  return ((position.currentPrice - position.entryPrice) / position.entryPrice) * 100
}

function getStatusClass(pnl: number) {
  return pnl >= 0
    ? 'bg-green-100 text-green-800'
    : 'bg-red-100 text-red-800'
}

async function updateStopLoss(position: Position) {
  try {
    await tradingStore.updatePosition({
      ...position,
      stopLoss: parseFloat(position.stopLoss as unknown as string)
    })
  } catch (err) {
    error.value = 'Не удалось обновить Stop Loss'
    console.error(err)
  }
}

async function updateTakeProfit(position: Position) {
  try {
    await tradingStore.updatePosition({
      ...position,
      takeProfit: parseFloat(position.takeProfit as unknown as string)
    })
  } catch (err) {
    error.value = 'Не удалось обновить Take Profit'
    console.error(err)
  }
}

async function closePosition(position: Position) {
  if (confirm('Вы уверены, что хотите закрыть позицию?')) {
    try {
      await tradingStore.closePosition(position.id)
    } catch (err) {
      error.value = 'Не удалось закрыть позицию'
      console.error(err)
    }
  }
}

function showDetails(position: Position) {
  selectedPosition.value = position
}

// Обновление цен в реальном времени
function startPriceUpdates() {
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
  }

  updateInterval.value = window.setInterval(async () => {
    if (!isUnmounted.value) {
      try {
        await tradingStore.fetchPositions()
      } catch (err) {
        console.error('Failed to update positions:', err)
      }
    }
  }, 5000)
}

async function fetchData() {
  if (isUnmounted.value) return

  isLoading.value = true
  error.value = null
  try {
    await Promise.all([
      tradingStore.fetchStrategies(),
      tradingStore.fetchPositions()
    ])
    startPriceUpdates()
  } catch (err) {
    error.value = 'Не удалось загрузить данные. Пожалуйста, попробуйте позже.'
    console.error('Failed to fetch data:', err)
  } finally {
    if (!isUnmounted.value) {
      isLoading.value = false
    }
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
