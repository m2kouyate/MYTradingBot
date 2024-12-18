<!-- components/strategy/BacktestResults.vue -->
<template>
  <div class="bg-white shadow rounded-lg divide-y divide-gray-200">
    <!-- Основные метрики -->
    <div class="p-6">
      <h3 class="text-lg font-medium text-gray-900">Основные показатели</h3>
      <dl class="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div v-for="metric in mainMetrics" :key="metric.name" class="relative overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:px-6">
          <dt class="text-sm font-medium text-gray-500 truncate">{{ metric.name }}</dt>
          <dd class="mt-1 text-2xl font-semibold text-gray-900" :class="metric.class">
            {{ metric.value }}
          </dd>
          <div v-if="metric.change" class="mt-1">
            <span
              class="text-sm font-medium"
              :class="metric.change.value >= 0 ? 'text-green-600' : 'text-red-600'"
            >
              {{ metric.change.value >= 0 ? '↑' : '↓' }} {{ formatPercent(Math.abs(metric.change.value)) }}
            </span>
            <span class="text-sm text-gray-500"> vs прошлый тест</span>
          </div>
        </div>
      </dl>
    </div>

    <!-- График эквити и распределение прибыли -->
    <div class="p-6">
      <div class="grid grid-cols-2 gap-6">
        <!-- График эквити -->
        <div>
          <h4 class="text-sm font-medium text-gray-900 mb-4">Кривая доходности</h4>
          <div class="h-64">
            <LineChart
              :data="results.equityCurve"
              :margin="{ top: 10, right: 10, bottom: 20, left: 60 }"
            >
              <XAxis dataKey="date" :tickFormatter="formatDate" />
              <YAxis :tickFormatter="formatMoney" />
              <Tooltip content="equityTooltip" />
              <Line
                type="monotone"
                dataKey="equity"
                stroke="#2563eb"
                :strokeWidth="2"
                :dot="false"
              />
              <ReferenceLine y={config.initialCapital} stroke="#9CA3AF" strokeDasharray="3 3" />
            </LineChart>
          </div>
        </div>

        <!-- Распределение прибыли -->
        <div>
          <h4 class="text-sm font-medium text-gray-900 mb-4">Распределение P&L</h4>
          <div class="h-64">
            <BarChart
              :data="profitDistribution"
              :margin="{ top: 10, right: 10, bottom: 20, left: 40 }"
            >
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#2563eb">
                <Cell
                  v-for="entry in profitDistribution"
                  :key="entry.range"
                  :fill="entry.range.includes('-') ? '#EF4444' : '#10B981'"
                />
              </Bar>
            </BarChart>
          </div>
        </div>
      </div>
    </div>

    <!-- Детальная статистика -->
    <div class="p-6">
      <h4 class="text-sm font-medium text-gray-900 mb-4">Детальная статистика</h4>
      <div class="grid grid-cols-3 gap-6">
        <!-- Статистика сделок -->
        <div>
          <h5 class="text-xs font-medium text-gray-500 uppercase mb-3">Сделки</h5>
          <dl class="space-y-2">
            <div v-for="stat in tradeStats" :key="stat.name" class="flex justify-between">
              <dt class="text-sm text-gray-600">{{ stat.name }}</dt>
              <dd class="text-sm font-medium text-gray-900">{{ stat.value }}</dd>
            </div>
          </dl>
        </div>

        <!-- Риск-метрики -->
        <div>
          <h5 class="text-xs font-medium text-gray-500 uppercase mb-3">Риск-метрики</h5>
          <dl class="space-y-2">
            <div v-for="metric in riskMetrics" :key="metric.name" class="flex justify-between">
              <dt class="text-sm text-gray-600">{{ metric.name }}</dt>
              <dd class="text-sm font-medium text-gray-900">{{ metric.value }}</dd>
            </div>
          </dl>
        </div>

        <!-- Временные метрики -->
        <div>
          <h5 class="text-xs font-medium text-gray-500 uppercase mb-3">Временные метрики</h5>
          <dl class="space-y-2">
            <div v-for="metric in timeMetrics" :key="metric.name" class="flex justify-between">
              <dt class="text-sm text-gray-600">{{ metric.name }}</dt>
              <dd class="text-sm font-medium text-gray-900">{{ metric.value }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>

    <!-- График ежемесячных результатов -->
    <div class="p-6">
      <h4 class="text-sm font-medium text-gray-900 mb-4">Результаты по месяцам</h4>
      <div class="h-64">
        <BarChart
          :data="monthlyResults"
          :margin="{ top: 10, right: 10, bottom: 20, left: 60 }"
        >
          <XAxis dataKey="month" />
          <YAxis :tickFormatter="formatMoney" />
          <Tooltip content="monthlyTooltip" />
          <Bar dataKey="pnl" :fill="(entry) => entry.pnl >= 0 ? '#10B981' : '#EF4444'" />
        </BarChart>
      </div>
    </div>

    <!-- Последние сделки -->
    <div class="p-6">
      <div class="sm:flex sm:items-center">
        <div class="sm:flex-auto">
          <h4 class="text-sm font-medium text-gray-900">Последние сделки</h4>
        </div>
        <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            @click="exportTrades"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowDownTrayIcon class="h-4 w-4 mr-2" />
            Экспорт
          </button>
        </div>
      </div>
      <div class="mt-4 -mx-6 overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th v-for="header in tradeHeaders" :key="header.key" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                {{ header.label }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="trade in results.trades.slice(-5)" :key="trade.entryDate">
              <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                {{ formatDate(trade.entryDate) }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                {{ trade.type }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                {{ formatPrice(trade.entryPrice) }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                {{ formatPrice(trade.exitPrice) }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm" :class="trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ formatMoney(trade.pnl) }}
              </td>
              <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                {{ formatDuration(trade.exitDate - trade.entryDate) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowDownTrayIcon } from '@heroicons/vue/24/outline'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, Cell } from 'recharts'
import type { BacktestConfig, BacktestResults } from '@/types/backtest'
import { formatDate, formatMoney, formatPrice, formatPercent } from '@/utils/formatters'
import { backtestService } from '@/services/backtestService'
import { useNotificationStore } from '@/stores/notification'

const props = defineProps<{
  results: BacktestResults
  config: BacktestConfig
  previousResults?: BacktestResults // Для сравнения с предыдущим тестом
}>()

const notificationStore = useNotificationStore()

// Основные метрики
const mainMetrics = computed(() => [
  {
    name: 'Общий P&L',
    value: formatMoney(props.results.totalPnl),
    class: props.results.totalPnl >= 0 ? 'text-green-600' : 'text-red-600',
    change: props.previousResults ? {
      value: ((props.results.totalPnl - props.previousResults.totalPnl) / Math.abs(props.previousResults.totalPnl)) * 100
    } : undefined
  },
  {
    name: 'ROI',
    value: formatPercent(props.results.roi),
    class: props.results.roi >= 0 ? 'text-green-600' : 'text-red-600',
    change: props.previousResults ? {
      value: props.results.roi - props.previousResults.roi
    } : undefined
  },
  {
    name: 'Коэфф. Шарпа',
    value: props.results.sharpeRatio.toFixed(2),
    class: props.results.sharpeRatio >= 1 ? 'text-green-600' :
           props.results.sharpeRatio >= 0 ? 'text-yellow-600' : 'text-red-600'
  },
  {
    name: 'Макс. просадка',
    value: formatPercent(props.results.maxDrawdown),
    class: 'text-red-600'
  }
])

// Распределение прибыли
const profitDistribution = computed(() => {
  const bins: Record<string, number> = {}
  const binSize = 100 // размер бина в базовой валюте

  props.results.trades.forEach(trade => {
    const binIndex = Math.floor(trade.pnl / binSize)
    const binKey = `${binIndex * binSize}-${(binIndex + 1) * binSize}`
    bins[binKey] = (bins[binKey] || 0) + 1
  })

  return Object.entries(bins)
    .map(([range, count]) => ({ range, count }))
    .sort((a, b) => {
      const aMin = parseInt(a.range.split('-')[0])
      const bMin = parseInt(b.range.split('-')[0])
      return aMin - bMin
    })
})

// Ежемесячные результаты
const monthlyResults = computed(() => {
  const monthly: Record<string, number> = {}

  props.results.trades.forEach(trade => {
    const month = new Date(trade.exitDate).toLocaleString('default', { month: 'short', year: '2-digit' })
    monthly[month] = (monthly[month] || 0) + trade.pnl
  })

  return Object.entries(monthly).map(([month, pnl]) => ({ month, pnl }))
})

// Статистика сделок
const tradeStats = computed(() => [
  {
    name: 'Всего сделок',
    value: props.results.totalTrades
  },
  {
    name: 'Win Rate',
    value: formatPercent(props.results.winRate)
  },
  {
    name: 'Profit Factor',
    value: props.results.profitFactor.toFixed(2)
  },
  {
    name: 'Средняя прибыль',
    value: formatMoney(props.results.statistics.averageWin)
  },
  {
    name: 'Средний убыток',
    value: formatMoney(props.results.statistics.averageLoss)
  }
])

// Риск-метрики
const riskMetrics = computed(() => [
  {
    name: 'Recovery Factor',
    value: props.results.statistics.recoveryFactor.toFixed(2)
  },
  {
    name: 'Средняя просадка',
    value: formatPercent(props.results.statistics.averageDrawdown)
  },
  {
    name: 'Макс. выигрыш',
    value: formatMoney(props.results.statistics.largestWin)
  },
  {
    name: 'Макс. проигрыш',
    value: formatMoney(props.results.statistics.largestLoss)
  }
])

// Временные метрики
const timeMetrics = computed(() => [
  {
    name: 'Среднее время в позиции',
    value: formatDuration(props.results.statistics.averageHoldingTime)
  },
  {
    name: 'Сделок в месяц',
    value: calculateMonthlyTrades()
  }
])

const tradeHeaders = [
  { key: 'date', label: 'Дата' },
  { key: 'type', label: 'Тип' },
  { key: 'entryPrice', label: 'Цена входа' },
  { key: 'exitPrice', label: 'Цена выхода' },
  { key: 'pnl', label: 'P&L' },
  { key: 'duration', label: 'Длительность' }
]

// Кастомные тултипы для графиков
const equityTooltip = ({ active, payload }: any) => {
  if (active && payload?.length) {
    return h('div', {
      class: 'bg-white p-2 shadow rounded border'
    }, [
      h('p', { class: 'text-sm text-gray-500' }, formatDate(payload[0].payload.date)),
      h('p', { class: 'text-sm font-medium text-gray-900' }, formatMoney(payload[0].value))
    ])
  }
  return null
}

const monthlyTooltip = ({ active, payload }: any) => {
  if (active && payload?.length) {
    return h('div', {
      class: 'bg-white p-2 shadow rounded border'
    }, [
      h('p', { class: 'text-sm text-gray-500' }, payload[0].payload.month),
      h('p', {
        class: `text-sm font-medium ${payload[0].value >= 0 ? 'text-green-600' : 'text-red-600'}`
      }, formatMoney(payload[0].value))
    ])
  }
  return null
}

// Утилиты
function formatDuration(ms: number): string {
  const hours = Math.floor(ms / (1000 * 60 * 60))
  const days = Math.floor(hours / 24)
  return days > 0 ? `${days}d` : `${hours}h`
}

function calculateMonthlyTrades(): number {
  const firstTrade = new Date(props.results.trades[0].entryDate)
  const lastTrade = new Date(props.results.trades[props.results.trades.length - 1].exitDate)
  const monthsDiff = (lastTrade.getTime() - firstTrade.getTime()) / (1000 * 60 * 60 * 24 * 30)
  return Math.round(props.results.totalTrades / monthsDiff)
}

// Экспорт данных
async function exportTrades() {
  try {
    const data = props.results.trades.map(trade => ({
      date: formatDate(trade.entryDate),
      type: trade.type,
      entryPrice: formatPrice(trade.entryPrice),
      exitPrice: formatPrice(trade.exitPrice),
      pnl: formatMoney(trade.pnl),
      duration: formatDuration(trade.exitDate - trade.entryDate)
    }))

    await backtestService.exportTradeHistory(data)
    notificationStore.showSuccess('История сделок успешно экспортирована')
  } catch (error) {
    notificationStore.showError('Ошибка при экспорте истории сделок')
  }
}
</script>