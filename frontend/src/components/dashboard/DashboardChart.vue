<!-- components/dashboard/DashboardChart.vue -->
<template>
  <div class="bg-white p-6 rounded-lg shadow">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
      <select
        v-model="selectedPeriod"
        class="rounded-md border-gray-300 text-sm focus:border-primary-500 focus:ring-primary-500"
      >
        <option value="day">24 часа</option>
        <option value="week">Неделя</option>
        <option value="month">Месяц</option>
        <option value="year">Год</option>
      </select>
    </div>

    <div class="h-64">
      <template v-if="isLoading">
        <SkeletonLoader
          width="full"
          :height="256"
        />
      </template>
      <template v-else>
        <Line
          :data="chartData"
          :options="chartOptions"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Line } from 'vue-chartjs'
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
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import { formatDate } from '@/utils/formatters'

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

interface ChartData {
  time: string
  value: number
}

const props = defineProps<{
  title: string
  isLoading?: boolean
  data?: ChartData[]
  valueFormatter?: (value: number) => string
}>()

const emit = defineEmits<{
  'period-change': [period: string]
}>()

const selectedPeriod = ref('day')

const formatTime = (time: string) => {
  const date = new Date(time)
  switch (selectedPeriod.value) {
    case 'day':
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    case 'week':
      return date.toLocaleDateString([], { weekday: 'short' })
    case 'month':
      return date.toLocaleDateString([], { day: 'numeric', month: 'short' })
    case 'year':
      return date.toLocaleDateString([], { month: 'short' })
    default:
      return time
  }
}

const chartData = computed(() => ({
  labels: props.data?.map(item => formatTime(item.time)) || [],
  datasets: [
    {
      label: props.title,
      data: props.data?.map(item => item.value) || [],
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
    mode: 'index',
    intersect: false,
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: (context: any) => {
          const value = context.raw
          return props.valueFormatter ? props.valueFormatter(value) : value
        }
      }
    }
  },
  scales: {
    y: {
      ticks: {
        callback: (value: number) => props.valueFormatter ? props.valueFormatter(value) : value
      }
    }
  }
}

watch(selectedPeriod, (newPeriod) => {
  emit('period-change', newPeriod)
})
</script>