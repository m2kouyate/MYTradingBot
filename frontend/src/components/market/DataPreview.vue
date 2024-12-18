<!-- components/market/DataPreview.vue -->
<template>
  <div class="bg-white shadow rounded-lg">
    <!-- Заголовок с метриками -->
    <div class="p-4 border-b border-gray-200">
      <div class="flex justify-between items-start">
        <div>
          <h3 class="text-lg font-medium text-gray-900">
            Предпросмотр данных {{ symbol }}
          </h3>
          <p class="mt-1 text-sm text-gray-500">
            {{ formatDateRange(startDate, endDate) }}
          </p>
        </div>
        <div class="flex gap-2">
          <button
            @click="validateData"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <CheckCircleIcon class="h-4 w-4 mr-1" />
            Проверить данные
          </button>
          <button
            @click="refreshData"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            :disabled="isLoading"
          >
            <ArrowPathIcon
              class="h-4 w-4 mr-1"
              :class="{ 'animate-spin': isLoading }"
            />
            Обновить
          </button>
        </div>
      </div>

      <!-- Метрики данных -->
      <div class="mt-4 grid grid-cols-4 gap-4">
        <div
          v-for="metric in dataMetrics"
          :key="metric.name"
          class="bg-gray-50 px-4 py-2 rounded-lg"
        >
          <dt class="text-sm text-gray-500">{{ metric.name }}</dt>
          <dd class="mt-1 text-lg font-semibold text-gray-900">{{ metric.value }}</dd>
        </div>
      </div>
    </div>

    <!-- Основной график -->
    <div class="p-4">
      <div class="h-96">
        <CandlestickChart
          :data="historicalData"
          :is-loading="isLoading"
          :selected-indicator="selectedIndicator"
          @time-range-change="handleTimeRangeChange"
        />
      </div>

      <!-- Индикаторы -->
      <div class="mt-4 flex gap-2">
        <button
          v-for="indicator in availableIndicators"
          :key="indicator.id"
          @click="toggleIndicator(indicator.id)"
          :class="[
            'px-3 py-1 rounded-full text-sm font-medium',
            selectedIndicator === indicator.id
              ? 'bg-primary-100 text-primary-800'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          ]"
        >
          {{ indicator.name }}
        </button>
      </div>
    </div>

    <!-- Статистика и проблемы -->
    <div class="p-4 border-t border-gray-200">
      <div class="grid grid-cols-2 gap-6">
        <!-- Статистика распределения -->
        <div>
          <h4 class="text-sm font-medium text-gray-900 mb-2">
            Распределение объемов
          </h4>
          <div class="h-48">
            <BarChart
              :data="volumeDistribution"
              :margin="{ top: 10, right: 10, bottom: 20, left: 40 }"
            >
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3B82F6" />
            </BarChart>
          </div>
        </div>

        <!-- Проблемы с данными -->
        <div>
          <h4 class="text-sm font-medium text-gray-900 mb-2">
            Обнаруженные проблемы
          </h4>
          <div class="space-y-2">
            <div
              v-for="(issue, index) in dataIssues"
              :key="index"
              :class="[
                'p-2 rounded-md text-sm',
                issue.type === 'error'
                  ? 'bg-red-50 text-red-700'
                  : 'bg-yellow-50 text-yellow-700'
              ]"
            >
              <div class="flex items-start">
                <component
                  :is="issue.type === 'error' ? ExclamationCircleIcon : ExclamationTriangleIcon"
                  class="h-5 w-5 mr-2 flex-shrink-0"
                />
                <span>{{ issue.message }}</span>
              </div>
            </div>
            <div
              v-if="dataIssues.length === 0"
              class="p-2 rounded-md bg-green-50 text-green-700 text-sm"
            >
              <div class="flex items-start">
                <CheckCircleIcon class="h-5 w-5 mr-2 flex-shrink-0" />
                <span>Проблем не обнаружено</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  CheckCircleIcon,
  ArrowPathIcon,
  ExclamationCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import type { HistoricalData } from '@/types/market'
import CandlestickChart from './CandlestickChart.vue'
import { validateHistoricalData } from '@/utils/dataValidation'
import { calculateVolumeDistribution } from '@/utils/dataAnalysis'
import { formatDateRange, formatNumber } from '@/utils/formatters'

const props = defineProps<{
  symbol: string
  startDate: Date
  endDate: Date
  source: string
  data: HistoricalData[]
}>()

const emit = defineEmits<{
  refresh: []
  'validation-complete': [issues: Array<{ type: string; message: string }>]
}>()

// Состояние
const isLoading = ref(false)
const selectedIndicator = ref<string | null>(null)
const dataIssues = ref<Array<{ type: 'error' | 'warning'; message: string }>>([])
const historicalData = ref<HistoricalData[]>(props.data)

// Доступные индикаторы
const availableIndicators = [
  { id: 'sma', name: 'SMA' },
  { id: 'ema', name: 'EMA' },
  { id: 'bollinger', name: 'Bollinger' },
  { id: 'volume', name: 'Volume' }
]

// Метрики данных
const dataMetrics = computed(() => [
  {
    name: 'Количество свечей',
    value: historicalData.value.length.toLocaleString()
  },
  {
    name: 'Средний объем',
    value: formatNumber(
      historicalData.value.reduce((sum, d) => sum + d.volume, 0) /
      historicalData.value.length
    )
  },
  {
    name: 'Пропуски данных',
    value: calculateDataGaps().length
  },
  {
    name: 'Аномальные свечи',
    value: detectAnomalies().length
  }
])

// Распределение объемов
const volumeDistribution = computed(() =>
  calculateVolumeDistribution(historicalData.value)
)

// Методы
async function refreshData() {
  isLoading.value = true
  try {
    emit('refresh')
  } finally {
    isLoading.value = false
  }
}

function validateData() {
  const issues = validateHistoricalData(historicalData.value)
  dataIssues.value = issues
  emit('validation-complete', issues)
}

function toggleIndicator(indicatorId: string) {
  selectedIndicator.value =
    selectedIndicator.value === indicatorId ? null : indicatorId
}

function handleTimeRangeChange(range: { start: Date; end: Date }) {
  // Обновляем видимый диапазон данных
}

function calculateDataGaps(): Array<{ start: Date; end: Date }> {
  const gaps = []
  for (let i = 1; i < historicalData.value.length; i++) {
    const expectedDiff = calculateExpectedTimeDiff(
      historicalData.value[i-1].timestamp
    )
    const actualDiff = historicalData.value[i].timestamp -
                      historicalData.value[i-1].timestamp

    if (actualDiff > expectedDiff * 1.5) {
      gaps.push({
        start: new Date(historicalData.value[i-1].timestamp),
        end: new Date(historicalData.value[i].timestamp)
      })
    }
  }
  return gaps
}

function detectAnomalies(): number[] {
  const anomalies = []
  const prices = historicalData.value.map(d => d.close)
  const mean = prices.reduce((a, b) => a + b) / prices.length
  const stdDev = Math.sqrt(
    prices.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / prices.length
  )

  historicalData.value.forEach((candle, i) => {
    if (
      Math.abs(candle.close - mean) > stdDev * 3 ||
      candle.high - candle.low > stdDev * 5
    ) {
      anomalies.push(i)
    }
  })

  return anomalies
}

function calculateExpectedTimeDiff(timestamp: number): number {
  // Рассчитываем ожидаемую разницу во времени на основе таймфрейма
  return 60000 // По умолчанию 1 минута
}

// Наблюдатели
watch(
  () => props.data,
  (newData) => {
    historicalData.value = newData
    validateData()
  }
)

// Инициализация
onMounted(() => {
  validateData()
})
</script>