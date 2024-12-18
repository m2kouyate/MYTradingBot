<!-- components/position/PositionChart.vue -->
<template>
  <div class="w-full h-full">
    <Line
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script setup lang="ts">
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
import type { Position } from '@/types/trading'
import { formatPrice } from '@/utils/formatters'
import { computed } from 'vue'
import annotationPlugin from 'chartjs-plugin-annotation'

// Регистрируем компоненты Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  annotationPlugin
)

const props = defineProps<{
  position: Position
  chartData: Array<{ time: string; price: number }>
}>()

const formatTime = (time: string) => {
  return new Date(time).toLocaleTimeString()
}

const transformedData = computed(() => ({
  labels: props.chartData.map(item => formatTime(item.time)),
  datasets: [
    {
      label: 'Цена',
      data: props.chartData.map(item => item.price),
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
        callback: (value: number) => formatPrice(value)
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          return `Цена: ${formatPrice(context.raw)}`
        }
      }
    },
    annotation: {
      annotations: {
        entryLine: {
          type: 'line',
          yMin: props.position.entryPrice,
          yMax: props.position.entryPrice,
          borderColor: '#6B7280',
          borderWidth: 1,
          borderDash: [5, 5],
          label: {
            content: 'Entry',
            enabled: true
          }
        },
        ...(props.position.stopLoss ? {
          stopLossLine: {
            type: 'line',
            yMin: props.position.stopLoss,
            yMax: props.position.stopLoss,
            borderColor: '#EF4444',
            borderWidth: 1,
            borderDash: [5, 5],
            label: {
              content: 'SL',
              enabled: true
            }
          }
        } : {}),
        ...(props.position.takeProfit ? {
          takeProfitLine: {
            type: 'line',
            yMin: props.position.takeProfit,
            yMax: props.position.takeProfit,
            borderColor: '#10B981',
            borderWidth: 1,
            borderDash: [5, 5],
            label: {
              content: 'TP',
              enabled: true
            }
          }
        } : {})
      }
    }
  }
}
</script>