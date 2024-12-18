<!-- components/strategy/StrategyStats.vue -->
<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-medium text-gray-900">{{ strategy.name }} - Статистика</h3>
      <button
        @click="exportStats"
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        <ArrowDownTrayIcon class="h-4 w-4 mr-2" />
        Экспорт
      </button>
    </div>

    <!-- Основные метрики -->
    <div class="grid grid-cols-4 gap-4 mb-6">
      <div>
        <p class="text-sm text-gray-500">Win Rate</p>
        <p class="mt-1 text-xl font-semibold text-gray-900">
          {{ formatPercent(stats.winRate) }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Всего сделок</p>
        <p class="mt-1 text-xl font-semibold text-gray-900">
          {{ stats.totalTrades }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Средний P&L</p>
        <p class="mt-1 text-xl font-semibold" :class="stats.avgPnl >= 0 ? 'text-green-600' : 'text-red-600'">
          {{ formatMoney(stats.avgPnl) }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Макс. просадка</p>
        <p class="mt-1 text-xl font-semibold text-red-600">
          {{ formatPercent(stats.drawdown) }}
        </p>
      </div>
    </div>

    <!-- График P&L -->
    <div class="h-64 mb-6">
      <Line
        :data="chartData"
        :options="chartOptions"
      />
    </div>

    <!-- Таблица сделок -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="header in tableHeaders"
              :key="header.key"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              :class="header.align === 'right' ? 'text-right' : ''"
            >
              {{ header.label }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="trade in recentTrades" :key="trade.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ formatDate(trade.date) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ trade.type }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
              {{ formatPrice(trade.entryPrice) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
              {{ trade.exitPrice ? formatPrice(trade.exitPrice) : '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right">
              <span :class="trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ formatMoney(trade.pnl) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowDownTrayIcon } from '@heroicons/vue/24/outline'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'vue-chartjs'
import { formatDate, formatMoney, formatPrice, formatPercent } from '@/utils/formatters'
import { ExportService } from '@/services/exportService'

// Регистрируем компоненты Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps<{
  strategy: Strategy
  stats: StrategyStats
  pnlHistory: Array<{ date: string; pnl: number }>
  recentTrades: Array<Trade>
}>()

const tableHeaders = [
  { key: 'date', label: 'Дата' },
  { key: 'type', label: 'Тип' },
  { key: 'entryPrice', label: 'Цена входа', align: 'right' },
  { key: 'exitPrice', label: 'Цена выхода', align: 'right' },
  { key: 'pnl', label: 'P&L', align: 'right' }
]

const chartData = computed(() => ({
  labels: props.pnlHistory.map(item => formatDate(item.date)),
  datasets: [
    {
      label: 'P&L',
      data: props.pnlHistory.map(item => item.pnl),
      borderColor: '#2563eb',
      tension: 0.4,
      fill: false
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index'
  },
  scales: {
    y: {
      ticks: {
        callback: (value: number) => formatMoney(value)
      }
    }
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: (context: any) => {
          return `P&L: ${formatMoney(context.raw)}`
        }
      }
    }
  }
}

async function exportStats() {
  const columns = [
    { key: 'date', label: 'Дата', format: formatDate },
    { key: 'type', label: 'Тип' },
    { key: 'entryPrice', label: 'Цена входа', format: formatPrice },
    { key: 'exitPrice', label: 'Цена выхода', format: (v: number | null) => v ? formatPrice(v) : '-' },
    { key: 'pnl', label: 'P&L', format: formatMoney }
  ]

  try {
    await ExportService.exportData(props.recentTrades, {
      filename: `${props.strategy.name}_trades_${formatDate(new Date())}`,
      format: 'xlsx',
      columns
    })
  } catch (error) {
    console.error('Failed to export data:', error)
  }
}
</script>