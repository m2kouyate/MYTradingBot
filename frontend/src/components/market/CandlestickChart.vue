<!-- components/market/CandlestickChart.vue -->
<template>
  <div class="relative">
    <!-- Основной график -->
    <div :id="chartId" class="w-full h-full" />

    <!-- Загрузка -->
    <div
      v-if="isLoading"
      class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center"
    >
      <div class="text-center">
        <svg
          class="animate-spin h-8 w-8 mx-auto text-primary-600"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        <p class="mt-2 text-sm text-gray-500">Загрузка данных...</p>
      </div>
    </div>

    <!-- Контролы -->
    <div
      v-if="!isLoading"
      class="absolute top-4 right-4 flex gap-2"
    >
      <button
        v-for="tf in timeframes"
        :key="tf"
        @click="setTimeframe(tf)"
        :class="[
          'px-2 py-1 text-xs font-medium rounded-md',
          selectedTimeframe === tf
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        {{ tf }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { createChart, IChartApi, ISeriesApi, Time } from 'lightweight-charts'
import { nanoid } from 'nanoid'
import type { HistoricalData } from '@/types/market'
import { calculateIndicators } from '@/utils/indicators'

const props = defineProps<{
  data: HistoricalData[]
  isLoading: boolean
  selectedIndicator: string | null
}>()

const emit = defineEmits<{
  'time-range-change': [range: { start: Date; end: Date }]
}>()

// Состояние
const chartId = ref(`chart-${nanoid()}`)
const chart = ref<IChartApi | null>(null)
const candlestickSeries = ref<ISeriesApi<'Candlestick'> | null>(null)
const indicatorSeries = ref<ISeriesApi<'Line'> | null>(null)
const volumeSeries = ref<ISeriesApi<'Histogram'> | null>(null)
const selectedTimeframe = ref('1h')
const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']

// Инициализация графика
onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chart.value) {
    chart.value.remove()
  }
})

function initChart() {
  const element = document.getElementById(chartId.value)
  if (!element) return

  // Создаем график
  chart.value = createChart(element, {
    layout: {
      background: { color: '#ffffff' },
      textColor: '#333333',
    },
    grid: {
      vertLines: { color: '#f0f0f0' },
      horzLines: { color: '#f0f0f0' },
    },
    crosshair: {
      mode: 0,
      vertLine: {
        color: '#758696',
        width: 1,
        style: 3,
        labelBackgroundColor: '#758696',
      },
      horzLine: {
        color: '#758696',
        width: 1,
        style: 3,
        labelBackgroundColor: '#758696',
      },
    },
    timeScale: {
      borderColor: '#f0f0f0',
      timeVisible: true,
      secondsVisible: false,
    },
  })

  // Добавляем серии
  candlestickSeries.value = chart.value.addCandlestickSeries({
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderVisible: false,
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
  })

  volumeSeries.value = chart.value.addHistogramSeries({
    color: '#26a69a',
    priceFormat: {
      type: 'volume',
    },
    priceScaleId: '',
    scaleMargins: {
      top: 0.8,
      bottom: 0,
    },
  })

  updateChartData()

  // Добавляем обработчики событий
  chart.value.timeScale().subscribeVisibleTimeRangeChange(handleTimeRangeChange)
}

// Обновление данных
function updateChartData() {
  if (!candlestickSeries.value || !volumeSeries.value) return

  const chartData = props.data.map(candle => ({
    time: candle.timestamp / 1000 as Time,
    open: candle.open,
    high: candle.high,
    low: candle.low,
    close: candle.close
  }))

  const volumeData = props.data.map(candle => ({
    time: candle.timestamp / 1000 as Time,
    value: candle.volume,
    color: candle.close >= candle.open ? '#26a69a' : '#ef5350'
  }))

  candlestickSeries.value.setData(chartData)
  volumeSeries.value.setData(volumeData)

  updateIndicator()
}

// Обработка индикаторов
function updateIndicator() {
  if (!chart.value || !props.selectedIndicator) {
    if (indicatorSeries.value) {
      chart.value?.removeSeries(indicatorSeries.value)
      indicatorSeries.value = null
    }
    return
  }

  const indicatorData = calculateIndicators(
    props.data,
    props.selectedIndicator
  )

  if (!indicatorSeries.value) {
    indicatorSeries.value = chart.value.addLineSeries({
      color: '#2962FF',
      lineWidth: 2,
    })
  }

  indicatorSeries.value.setData(
    indicatorData.map(point => ({
      time: point.timestamp / 1000 as Time,
      value: point.value
    }))
  )
}

// Обработчики событий
function handleResize() {
  if (chart.value) {
    const element = document.getElementById(chartId.value)
    if (element) {
      chart.value.applyOptions({
        width: element.clientWidth,
        height: element.clientHeight
      })
    }
  }
}

function handleTimeRangeChange(range: { from: Time; to: Time }) {
  emit('time-range-change', {
    start: new Date((range.from as number) * 1000),
    end: new Date((range.to as number) * 1000)
  })
}

function setTimeframe(tf: string) {
  selectedTimeframe.value = tf
  // Здесь можно добавить логику изменения таймфрейма
}

// Наблюдатели
watch(() => props.data, updateChartData)
watch(() => props.selectedIndicator, updateIndicator)
</script>
