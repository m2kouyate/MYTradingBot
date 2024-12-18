<!-- components/strategy/BacktestComparison.vue -->
<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h3 class="text-lg font-medium text-gray-900">Сравнение бэктестов</h3>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
        <button
          @click="exportComparison"
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <ArrowDownTrayIcon class="h-4 w-4 mr-2" />
          Экспорт сравнения
        </button>
      </div>
    </div>

    <!-- Основные метрики -->
    <div class="mt-6">
      <h4 class="text-sm font-medium text-gray-900 mb-4">Сравнение метрик</h4>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Метрика
              </th>
              <th
                v-for="(result, index) in results"
                :key="index"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase"
              >
                Тест {{ index + 1 }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Разница
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="metric in comparisonMetrics" :key="metric.name">
              <td class="px-6 py-4 text-sm text-gray-900">
                {{ metric.name }}
              </td>
              <td
                v-for="(value, index) in metric.values"
                :key="index"
                class="px-6 py-4 text-sm"
                :class="metric.getValueClass?.(value)"
              >
                {{ metric.format ? metric.format(value) : value }}
              </td>
              <td
                class="px-6 py-4 text-sm"
                :class="metric.getDiffClass?.(metric.difference)"
              >
                {{ metric.formatDiff ? metric.formatDiff(metric.difference) : metric.difference }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Графики сравнения -->
    <div class="mt-6 grid grid-cols-2 gap-6">
      <!-- Сравнение эквити -->
      <div>
        <h4 class="text-sm font-medium text-gray-900 mb-4">Сравнение кривых доходности</h4>
        <div class="h-64">
          <LineChart
            :data="normalizedEquityCurves"
            :margin="{ top: 10, right: 10, bottom: 20, left: 40 }"
          >
            <XAxis dataKey="date" :tickFormatter="formatDate" />
            <YAxis :tickFormatter="(value) => `${value}%`" />
            <Tooltip content="equityComparisonTooltip" />
            <Legend />
            <Line
              v-for="(result, index) in results"
              :key="index"
              type="monotone"
              :dataKey="`test${index + 1}`"
              :stroke="getLineColor(index)"
              :strokeWidth="2"
              :dot="false"
              :name="`Тест ${index + 1}`"
            />
          </LineChart>
        </div>
      </div>

      <!-- Сравнение месячных результатов -->
      <div>
        <h4 class="text-sm font-medium text-gray-900 mb-4">Сравнение месячных результатов</h4>
        <div class="h-64">
          <BarChart
            :data="monthlyComparison"
            :margin="{ top: 10, right: 10, bottom: 20, left: 40 }"
          >
            <XAxis dataKey="month" />
            <YAxis :tickFormatter="formatMoney" />
            <Tooltip content="monthlyComparisonTooltip" />
            <Legend />
            <Bar
              v-for="(result, index) in results"
              :key="index"
              :dataKey="`test${index + 1}`"
              :fill="getBarColor(index)"
              :name="`Тест ${index + 1}`"
            />
          </BarChart>
        </div>
      </div>
    </div>

    <!-- Параметры тестов -->
    <div class="mt-6">
      <h4 class="text-sm font-medium text-gray-900 mb-4">Параметры тестов</h4>
      <div class="grid grid-cols-2 gap-6">
        <div
          v-for="(result, index) in results"
          :key="index"
          class="bg-gray-50 rounded-lg p-4"
        >
          <h5 class="text-sm font-medium text-gray-900 mb-3">Тест {{ index + 1 }}</h5>
          <dl class="grid grid-cols-2 gap-4">
            <div v-for="(value, key) in result.config.parameters" :key="key">
              <dt class="text-sm text-gray-500">{{ formatParameterName(key) }}</dt>
              <dd class="mt-1 text-sm font-medium text-gray-900">{{ value }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { ArrowDownTrayIcon } from '@heroicons/vue/24/outline'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import type { BacktestResults, BacktestConfig } from '@/types/backtest'
import { formatDate, formatMoney, formatPercent } from '@/utils/formatters'
import { useNotificationStore } from '@/stores/notification'

interface BacktestWithConfig {
  results: BacktestResults
  config: BacktestConfig
}

const props = defineProps<{
  results: BacktestWithConfig[]
}>()

const notificationStore = useNotificationStore()

// Метрики для сравнения
const comparisonMetrics = computed(() => [
  {
    name: 'Общий P&L',
    values: props.results.map(r => r.results.totalPnl),
    format: formatMoney,
    getValueClass: (value: number) => value >= 0 ? 'text-green-600' : 'text-red-600',
    difference: calculatePnlDifference(),
    formatDiff: (diff: number) => `${diff >= 0 ? '+' : ''}${formatMoney(diff)}`,
    getDiffClass: (diff: number) => diff >= 0 ? 'text-green-600' : 'text-red-600'
  },
  {
    name: 'ROI',
    values: props.results.map(r => r.results.roi),
    format: formatPercent,
    getValueClass: (value: number) => value >= 0 ? 'text-green-600' : 'text-red-600',
    difference: calculateRoiDifference(),
    formatDiff: (diff: number) => `${diff >= 0 ? '+' : ''}${formatPercent(diff)}`,
    getDiffClass: (diff: number) => diff >= 0 ? 'text-green-600' : 'text-red-600'
  },
  {
    name: 'Коэфф. Шарпа',
    values: props.results.map(r => r.results.sharpeRatio),
    format: (value: number) => value.toFixed(2),
    getValueClass: (value: number) =>
      value >= 1 ? 'text-green-600' :
      value >= 0 ? 'text-yellow-600' : 'text-red-600',
    difference: calculateSharpeDifference(),
    formatDiff: (diff: number) => diff.toFixed(2),
    getDiffClass: (diff: number) => diff >= 0 ? 'text-green-600' : 'text-red-600'
  },
  {
    name: 'Макс. просадка',
    values: props.results.map(r => r.results.maxDrawdown),
    format: formatPercent,
    getValueClass: () => 'text-red-600',
    difference: calculateDrawdownDifference(),
    formatDiff: (diff: number) => `${diff >= 0 ? '+' : ''}${formatPercent(diff)}`,
    getDiffClass: (diff: number) => diff <= 0 ? 'text-green-600' : 'text-red-600'
  },
  {
    name: 'Win Rate',
    values: props.results.map(r => r.results.winRate),
    format: formatPercent,
    difference: calculateWinRateDifference(),
    formatDiff: (diff: number) => `${diff >= 0 ? '+' : ''}${formatPercent(diff)}`,
    getDiffClass: (diff: number) => diff >= 0 ? 'text-green-600' : 'text-red-600'
  }
])

// Нормализованные кривые доходности (в процентах от начального капитала)
const normalizedEquityCurves = computed(() => {
  const allDates = new Set<string>()
  const curves: Record<string, Record<string, number>> = {}

  // Собираем все даты и нормализуем значения
  props.results.forEach((result, index) => {
    result.results.equityCurve.forEach(point => {
      allDates.add(point.date)
      if (!curves[point.date]) {
        curves[point.date] = {}
      }
      const normalizedValue = ((point.equity - result.config.initialCapital) / result.config.initialCapital) * 100
      curves[point.date][`test${index + 1}`] = normalizedValue
    })
  })

  // Преобразуем в массив для графика
  return Array.from(allDates)
    .sort()
    .map(date => ({
      date,
      ...curves[date]
    }))
})

// Сравнение месячных результатов
const monthlyComparison = computed(() => {
  const monthlyData: Record<string, Record<string, number>> = {}

  props.results.forEach((result, index) => {
    result.results.trades.forEach(trade => {
      const month = new Date(trade.exitDate).toLocaleString('default', { month: 'short', year: '2-digit' })
      if (!monthlyData[month]) {
        monthlyData[month] = {}
      }
      monthlyData[month][`test${index + 1}`] = (monthlyData[month][`test${index + 1}`] || 0) + trade.pnl
    })
  })

  return Object.entries(monthlyData)
    .map(([month, data]) => ({
      month,
      ...data
    }))
    .sort((a, b) => new Date(a.month) - new Date(b.month))
})

// Кастомные тултипы для графиков
const equityComparisonTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return h('div', {
      class: 'bg-white p-2 shadow rounded border'
    }, [
      h('p', { class: 'text-sm text-gray-500' }, formatDate(label)),
      ...payload.map((entry: any) =>
        h('p', {
          class: `text-sm font-medium ${entry.value >= 0 ? 'text-green-600' : 'text-red-600'}`
        }, `${entry.name}: ${entry.value.toFixed(2)}%`)
      )
    ])
  }
  return null
}

const monthlyComparisonTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return h('div', {
      class: 'bg-white p-2 shadow rounded border'
    }, [
      h('p', { class: 'text-sm text-gray-500' }, label),
      ...payload.map((entry: any) =>
        h('p', {
          class: `text-sm font-medium ${entry.value >= 0 ? 'text-green-600' : 'text-red-600'}`
        }, `${entry.name}: ${formatMoney(entry.value)}`)
      )
    ])
  }
  return null
}

// Утилиты
function calculatePnlDifference(): number {
  if (props.results.length < 2) return 0
  return props.results[1].results.totalPnl - props.results[0].results.totalPnl
}

function calculateRoiDifference(): number {
  if (props.results.length < 2) return 0
  return props.results[1].results.roi - props.results[0].results.roi
}

function calculateSharpeDifference(): number {
  if (props.results.length < 2) return 0
  return props.results[1].results.sharpeRatio - props.results[0].results.sharpeRatio
}

function calculateDrawdownDifference(): number {
  if (props.results.length < 2) return 0
  return props.results[1].results.maxDrawdown - props.results[0].results.maxDrawdown
}

function calculateWinRateDifference(): number {
  if (props.results.length < 2) return 0
  return props.results[1].results.winRate - props.results[0].results.winRate
}

function getLineColor(index: number): string {
  const colors = ['#2563eb', '#10B981', '#6366F1', '#EC4899']
  return colors[index % colors.length]
}

function getBarColor(index: number): string {
  const colors = ['#93C5FD', '#86EFAC', '#A5B4FC', '#F9A8D4']
  return colors[index % colors.length]
}

function formatParameterName(key: string): string {
  return key
    .split(/(?=[A-Z])/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Экспорт сравнения
async function exportComparison() {
  try {
    // Подготавливаем данные для экспорта
    const data = comparisonMetrics.value.map(metric => ({
      metric: metric.name,
      ...metric.values.reduce((acc, value, index) => ({
        ...acc,
        [`test${index + 1}`]: metric.format ? metric.format(value) : value
      }), {}),
      difference: metric.formatDiff ? metric.formatDiff(metric.difference) : metric.difference
    }))

    const fileName = `backtest_comparison_${formatDate(new Date())}`
    await backtestService.exportComparison(data, fileName)
    notificationStore.showSuccess('Сравнение успешно экспортировано')
  } catch (error) {
    notificationStore.showError('Ошибка при экспорте сравнения')
  }
}
</script>