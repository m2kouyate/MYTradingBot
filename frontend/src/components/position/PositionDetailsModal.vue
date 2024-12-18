<!-- components/position/PositionDetailsModal.vue -->
<template>
  <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
  <div class="fixed inset-0 z-10 overflow-y-auto">
    <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
      <div class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6">
        <div>
          <div class="absolute right-0 top-0 pr-4 pt-4">
            <button
              type="button"
              @click="emit('close')"
              class="rounded-md bg-white text-gray-400 hover:text-gray-500"
            >
              <span class="sr-only">Закрыть</span>
              <X class="h-6 w-6" aria-hidden="true" />
            </button>
          </div>

          <h3 class="text-xl font-semibold leading-6 text-gray-900 mb-4">
            {{ position.symbol }} - Детали позиции
          </h3>

          <!-- График цены -->
          <div class="mb-6">
            <h4 class="text-sm font-medium text-gray-900 mb-2">График цены</h4>
            <div class="h-64">
              <PositionChart
                :position="position"
                :chartData="chartData"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-6">
            <!-- Основная информация -->
            <div class="space-y-4">
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-2">Основная информация</h4>
                <dl class="space-y-2">
                  <div class="flex justify-between">
                    <dt class="text-sm text-gray-500">Стратегия</dt>
                    <dd class="text-sm text-gray-900">{{ getStrategyName(position.strategyId) }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-sm text-gray-500">Дата открытия</dt>
                    <dd class="text-sm text-gray-900">{{ formatDate(position.createdAt) }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-sm text-gray-500">Срок удержания</dt>
                    <dd class="text-sm text-gray-900">{{ getHoldingPeriod(position.createdAt) }}</dd>
                  </div>
                </dl>
              </div>

              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-2">Цены и объем</h4>
                <dl class="space-y-2">
                  <div class="flex justify-between">
                    <dt class="text-sm text-gray-500">Цена входа</dt>
                    <dd class="text-sm text-gray-900">{{ formatPrice(position.entryPrice) }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-sm text-gray-500">Текущая цена</dt>
                    <dd class="text-sm text-gray-900">{{ formatPrice(position.currentPrice) }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-sm text-gray-500">Количество</dt>
                    <dd class="text-sm text-gray-900">{{ formatQuantity(position.quantity) }}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <!-- P&L и риск-менеджмент -->
            <div class="space-y-4">
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-2">P&L</h4>
                <dl class="space-y-2">
                  <div class="flex justify-between">
                    <dt class="text-sm text-gray-500">Нереализованный P&L</dt>
                    <dd
                      class="text-sm font-medium"
                      :class="position.unrealizedPnl >= 0 ? 'text-green-600' : 'text-red-600'"
                    >
                      {{ formatMoney(position.unrealizedPnl) }}
                    </dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-sm text-gray-500">Процент возврата</dt>
                    <dd
                      class="text-sm font-medium"
                      :class="getPositionReturn(position) >= 0 ? 'text-green-600' : 'text-red-600'"
                    >
                      {{ formatPercent(getPositionReturn(position)) }}
                    </dd>
                  </div>
                </dl>
              </div>

              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-2">Риск-менеджмент</h4>
                <dl class="space-y-4">
                  <div>
                    <dt class="text-sm text-gray-500 mb-1">Stop Loss</dt>
                    <dd class="flex items-center gap-2">
                      <input
                        type="number"
                        v-model="localStopLoss"
                        class="block w-32 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                        step="0.01"
                      />
                      <span class="text-sm text-gray-500">
                        ({{ calculatePotentialLoss }}%)
                      </span>
                      <button
                        @click="updateStopLoss"
                        class="ml-2 inline-flex items-center rounded bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10"
                      >
                        Обновить
                      </button>
                    </dd>
                  </div>
                  <div>
                    <dt class="text-sm text-gray-500 mb-1">Take Profit</dt>
                    <dd class="flex items-center gap-2">
                      <input
                        type="number"
                        v-model="localTakeProfit"
                        class="block w-32 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                        step="0.01"
                      />
                      <span class="text-sm text-gray-500">
                        ({{ calculatePotentialProfit }}%)
                      </span>
                      <button
                        @click="updateTakeProfit"
                        class="ml-2 inline-flex items-center rounded bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10"
                      >
                        Обновить
                      </button>
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>

          <!-- Алерты и уведомления -->
          <div class="mt-6">
            <h4 class="text-sm font-medium text-gray-900 mb-2">Алерты</h4>
            <div class="space-y-2">
              <label class="flex items-center gap-2">
                <input
                  type="checkbox"
                  v-model="priceAlertEnabled"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="text-sm text-gray-900">Уведомлять при изменении цены более чем на</span>
                <input
                  type="number"
                  v-model="priceAlertThreshold"
                  class="block w-20 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                  step="0.1"
                  min="0"
                />
                <span class="text-sm text-gray-900">%</span>
              </label>
            </div>
          </div>

          <!-- История изменений -->
          <div class="mt-6">
            <h4 class="text-sm font-medium text-gray-900 mb-2">История изменений</h4>
            <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
              <table class="min-w-full divide-y divide-gray-300">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Дата</th>
                    <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Тип</th>
                    <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Значение</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                  <tr v-for="change in positionHistory" :key="change.id">
                    <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900">
                      {{ formatDate(change.timestamp) }}
                    </td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      {{ change.type }}
                    </td>
                    <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                      {{ formatChangeValue(change) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Действия -->
          <div class="mt-6 flex gap-3 justify-end">
            <button
              @click="emit('close')"
              class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            >
              Закрыть
            </button>
            <button
              @click="confirmClose"
              class="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500"
            >
              Закрыть позицию
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { X } from 'lucide-vue-next'
import type { Position, PositionChange } from '@/types/trading'
import { useTradingStore } from '@/stores/trading'
import PositionChart from './PositionChart.vue'
import { formatDate, formatMoney, formatPrice, formatQuantity, formatPercent } from '@/utils/formatters'

const props = defineProps<{
  position: Position
}>()

const emit = defineEmits<{
  close: []
}>()

const tradingStore = useTradingStore()
const chartData = ref([])
const positionHistory = ref<PositionChange[]>([])
const localStopLoss = ref(props.position.stopLoss)
const localTakeProfit = ref(props.position.takeProfit)
const priceAlertEnabled = ref(false)
const priceAlertThreshold = ref(1)

// Расчет процентных изменений
const calculatePotentialLoss = computed(() => {
  return ((localStopLoss.value - props.position.entryPrice) / props.position.entryPrice * 100).toFixed(2)
})

const calculatePotentialProfit = computed(() => {
  return ((localTakeProfit.value - props.position.entryPrice) / props.position.entryPrice * 100).toFixed(2)
})

function getPositionReturn(position: Position) {
  return ((position.currentPrice - position.entryPrice) / position.entryPrice) * 100
}

function getStrategyName(strategyId: number) {
  const strategy = tradingStore.strategies.find(s => s.id === strategyId)
  return strategy?.name || 'Неизвестная стратегия'
}

function getHoldingPeriod(createdAt: string) {
  const start = new Date(createdAt)
  const now = new Date()
  const days = Math.floor((now.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
  return `${days} дн.`
}

async function updateStopLoss() {
  await tradingStore.updatePosition({
    ...props.position,
    stopLoss: localStopLoss.value
  })
}

async function updateTakeProfit() {
  await tradingStore.updatePosition({
    ...props.position,
    takeProfit: localTakeProfit.value
  })
}

function formatChangeValue(change: PositionChange) {
  switch (change.type) {
    case 'STOP_LOSS':
    case 'TAKE_PROFIT':
    case 'PRICE':
      return formatPrice(change.value)
    default:
      return change.value
  }
}

function confirmClose() {
  if (confirm('Вы уверены, что хотите закрыть позицию?')) {
    tradingStore.closePosition(props.position.id)
    emit('close')
  }
}

onMounted(async () => {
  // Загрузка исторических данных и изменений позиции
  chartData.value = await tradingStore.fetchPositionHistory(props.position.id)
  positionHistory.value = await tradingStore.fetchPositionChanges(props.position.id)
})
</script>