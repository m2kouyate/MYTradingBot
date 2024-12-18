<!-- components/strategy/BacktestDialog.vue -->
<template>
  <Dialog as="div" class="relative z-50" @close="close">
    <div class="fixed inset-0 bg-black/30" />

    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4">
        <DialogPanel class="w-full max-w-4xl transform rounded-lg bg-white p-6 shadow-xl transition-all">
          <DialogTitle class="text-lg font-medium text-gray-900">
            Бэктестинг стратегии "{{ strategy.name }}"
          </DialogTitle>

          <!-- Параметры бэктеста -->
          <div class="mt-4 grid grid-cols-2 gap-6">
            <!-- Период тестирования -->
            <div>
              <label class="block text-sm font-medium text-gray-700">Период</label>
              <div class="mt-2 flex gap-4">
                <div>
                  <label class="block text-xs text-gray-500">От</label>
                  <input
                    type="date"
                    v-model="config.startDate"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label class="block text-xs text-gray-500">До</label>
                  <input
                    type="date"
                    v-model="config.endDate"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>

            <!-- Начальный капитал -->
            <div>
              <label class="block text-sm font-medium text-gray-700">Начальный капитал</label>
              <div class="mt-2">
                <input
                  type="number"
                  v-model="config.initialCapital"
                  min="0"
                  step="100"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
            </div>
          </div>

          <!-- Параметры стратегии -->
          <div class="mt-6">
            <h4 class="text-sm font-medium text-gray-900">Параметры стратегии</h4>
            <div class="mt-2 grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-700">Take Profit (%)</label>
                <input
                  type="number"
                  v-model="config.parameters.takeProfit"
                  step="0.1"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
              <div>
                <label class="block text-sm text-gray-700">Stop Loss (%)</label>
                <input
                  type="number"
                  v-model="config.parameters.stopLoss"
                  step="0.1"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
              <!-- Добавить другие параметры стратегии -->
            </div>
          </div>

          <!-- Дополнительные настройки -->
          <div class="mt-6">
            <h4 class="text-sm font-medium text-gray-900">Дополнительные настройки</h4>
            <div class="mt-2 space-y-3">
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="config.includeCommissions"
                  class="form-checkbox h-4 w-4 text-primary-600 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-700">Учитывать комиссии</span>
              </label>
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="config.optimizeParameters"
                  class="form-checkbox h-4 w-4 text-primary-600 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-700">Оптимизировать параметры</span>
              </label>
            </div>
          </div>

          <!-- Результаты бэктеста -->
          <div v-if="results" class="mt-6">
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-4">Результаты тестирования</h4>
              <div class="grid grid-cols-4 gap-4">
                <div>
                  <p class="text-sm text-gray-500">Общий P&L</p>
                  <p class="mt-1 text-lg font-medium" :class="results.totalPnl >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatMoney(results.totalPnl) }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">ROI</p>
                  <p class="mt-1 text-lg font-medium" :class="results.roi >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatPercent(results.roi) }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Шарп</p>
                  <p class="mt-1 text-lg font-medium text-gray-900">
                    {{ results.sharpeRatio.toFixed(2) }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Макс. просадка</p>
                  <p class="mt-1 text-lg font-medium text-red-600">
                    {{ formatPercent(results.maxDrawdown) }}
                  </p>
                </div>
              </div>

              <!-- График эквити -->
              <div class="mt-4 h-64">
                <LineChart
                  :data="results.equityCurve"
                  :margin="{ top: 20, right: 20, bottom: 20, left: 60 }"
                >
                  <XAxis dataKey="date" :tickFormatter="formatDate" />
                  <YAxis :tickFormatter="formatMoney" />
                  <Tooltip content={CustomTooltip} />
                  <Line
                    type="monotone"
                    dataKey="equity"
                    stroke="#2563eb"
                    :dot="false"
                    :strokeWidth="2"
                  />
                </LineChart>
              </div>
            </div>
          </div>

          <!-- Действия -->
          <div class="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              @click="close"
              class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
            >
              {{ results ? 'Закрыть' : 'Отмена' }}
            </button>
            <button
              v-if="!isRunning && !results"
              type="button"
              @click="runBacktest"
              class="inline-flex justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700"
            >
              Запустить тест
            </button>
            <button
              v-if="results"
              type="button"
              @click="saveResults"
              class="inline-flex justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-700"
            >
              Сохранить результаты
            </button>
          </div>
        </DialogPanel>
      </div>
    </div>

    <!-- Прогресс бэктеста -->
    <BacktestProgress
      v-if="isRunning"
      :progress="progress"
      :status="status"
    />
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle
} from '@headlessui/vue'
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts'
import { useTradingStore } from '@/stores/trading'
import type { Strategy } from '@/types/trading'
import BacktestProgress from './BacktestProgress.vue'
import { formatDate, formatMoney, formatPercent } from '@/utils/formatters'

const props = defineProps<{
  strategy: Strategy
}>()

const emit = defineEmits<{
  close: []
  complete: [results: BacktestResults]
}>()

const tradingStore = useTradingStore()
const isRunning = ref(false)
const progress = ref(0)
const status = ref('')
const results = ref<BacktestResults | null>(null)

const config = ref<BacktestConfig>({
  startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 дней назад
  endDate: new Date().toISOString().split('T')[0],
  initialCapital: 10000,
  parameters: {
    takeProfit: props.strategy.takeProfit,
    stopLoss: props.strategy.stopLoss
  },
  includeCommissions: true,
  optimizeParameters: false
})

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload?.length) {
    return h('div', {
      class: 'bg-white p-2 shadow rounded border'
    }, [
      h('p', {
        class: 'text-sm text-gray-500'
      }, formatDate(payload[0].payload.date)),
      h('p', {
        class: 'text-sm font-medium text-gray-900'
      }, formatMoney(payload[0].value))
    ])
  }
  return null
}

async function runBacktest() {
  isRunning.value = true
  progress.value = 0
  results.value = null

  try {
    // Начинаем с загрузки исторических данных
    status.value = 'Загрузка исторических данных...'
    const historicalData = await tradingStore.fetchHistoricalData(
      props.strategy.symbol,
      config.value.startDate,
      config.value.endDate
    )

    // Если включена оптимизация параметров
    if (config.value.optimizeParameters) {
      status.value = 'Оптимизация параметров...'
      const optimizedParams = await tradingStore.optimizeStrategyParameters(
        props.strategy.id,
        historicalData,
        config.value,
        (p) => {
          progress.value = p * 0.5 // Первые 50% прогресса
        }
      )
      config.value.parameters = { ...config.value.parameters, ...optimizedParams }
    }

    // Запускаем бэктест
    status.value = 'Выполнение бэктеста...'
    results.value = await tradingStore.runBacktest(
      props.strategy.id,
      historicalData,
      config.value,
      (p) => {
        progress.value = config.value.optimizeParameters ? 50 + p * 0.5 : p
      }
    )

    status.value = 'Анализ результатов...'
  } catch (error) {
    console.error('Backtest error:', error)
    tradingStore.notificationStore.showError('Ошибка при выполнении бэктеста')
  } finally {
    isRunning.value = false
  }
}

async function saveResults() {
  if (!results.value) return

  try {
    await tradingStore.saveBacktestResults(props.strategy.id, {
      date: new Date().toISOString(),
      config: config.value,
      results: results.value
    })

    tradingStore.notificationStore.showSuccess('Результаты бэктеста сохранены')
    emit('complete', results.value)
    close()
  } catch (error) {
    console.error('Save results error:', error)
    tradingStore.notificationStore.showError('Ошибка при сохранении результатов')
  }
}

function close() {
  if (!isRunning.value) {
    emit('close')
  }
}

// Следим за изменением параметров оптимизации
watch(() => config.value.optimizeParameters, (newValue) => {
  if (results.value) {
    results.value = null // Сбрасываем результаты при изменении настроек
  }
})
</script>
