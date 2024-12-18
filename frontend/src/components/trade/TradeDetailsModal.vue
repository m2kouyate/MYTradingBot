<!-- components/trade/TradeDetailsModal.vue -->
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
              <XMarkIcon class="h-6 w-6" aria-hidden="true" />
            </button>
          </div>

          <h3 class="text-xl font-semibold leading-6 text-gray-900 mb-4">
            Детали сделки #{{ trade.id }}
          </h3>

          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">Стратегия</p>
                <p class="mt-1 text-sm text-gray-900">{{ getStrategyName(trade.strategyId) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Символ</p>
                <p class="mt-1 text-sm text-gray-900">{{ trade.symbol }}</p>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">Дата открытия</p>
                <p class="mt-1 text-sm text-gray-900">{{ formatDate(trade.createdAt) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Дата закрытия</p>
                <p class="mt-1 text-sm text-gray-900">
                  {{ trade.closedAt ? formatDate(trade.closedAt) : '-' }}
                </p>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-4">
              <div>
                <p class="text-sm text-gray-500">Цена входа</p>
                <p class="mt-1 text-sm text-gray-900">{{ formatPrice(trade.entryPrice) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Цена выхода</p>
                <p class="mt-1 text-sm text-gray-900">
                  {{ trade.exitPrice ? formatPrice(trade.exitPrice) : '-' }}
                </p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Объём</p>
                <p class="mt-1 text-sm text-gray-900">{{ formatQuantity(trade.quantity) }}</p>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">P&L</p>
                <p
                  class="mt-1 text-sm font-semibold"
                  :class="(trade.pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'"
                >
                  {{ formatMoney(trade.pnl) }}
                </p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Статус</p>
                <p class="mt-1">
                  <span
                    :class="[
                      trade.status === 'OPEN' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800',
                      'inline-flex rounded-full px-2 py-1 text-xs font-semibold'
                    ]"
                  >
                    {{ trade.status }}
                  </span>
                </p>
              </div>
            </div>

            <!-- График цены -->
            <div class="mt-6">
              <h4 class="text-sm font-medium text-gray-900 mb-2">График цены</h4>
              <div class="h-64">
                <TradeChart
                  :trade="trade"
                  :chartData="chartData"
                />
              </div>
            </div>

            <!-- Примечания -->
            <div class="mt-4">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Примечания</h4>
              <div class="rounded-md bg-gray-50 p-4">
                <div class="text-sm text-gray-700">
                  {{ trade.notes || 'Нет примечаний' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import type { Trade } from '@/types/trading'
import { useTradingStore } from '@/stores/trading'
import TradeChart from './TradeChart.vue'
import { formatDate, formatMoney, formatPrice, formatQuantity } from '@/utils/formatters'

const props = defineProps<{
  trade: Trade
}>()

const emit = defineEmits<{
  close: []
}>()

const tradingStore = useTradingStore()
const chartData = ref([])

const getStrategyName = (strategyId: number) => {
  const strategy = tradingStore.strategies.find(s => s.id === strategyId)
  return strategy?.name || 'Неизвестная стратегия'
}

onMounted(async () => {
  // Здесь мы бы загрузили исторические данные для графика
  chartData.value = await tradingStore.fetchTradeHistory(props.trade.id)
})
</script>