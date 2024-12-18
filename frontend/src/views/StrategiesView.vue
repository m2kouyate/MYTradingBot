<!-- views/StrategiesView.vue -->
<template>
  <div>
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-semibold text-gray-900">Торговые стратегии</h1>
      <button
        @click="showCreateModal = true"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        <Plus class="-ml-1 mr-2 h-5 w-5" />
        Создать стратегию
      </button>
    </div>

    <!-- Фильтры -->
    <StrategyFilters
      v-model:filters="filters"
      class="mt-6"
    />

    <LoadingSpinner v-if="isLoading" text="Загрузка стратегий..." />

    <ErrorState
      v-else-if="error"
      title="Ошибка загрузки стратегий"
      :message="error"
      @retry="fetchData"
    />

    <template v-else>
      <!-- Пустое состояние -->
      <div v-if="!hasStrategies" class="text-center py-12 bg-white mt-8 rounded-lg shadow">
        <Lightbulb class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">Нет стратегий</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ hasFilters ? 'Нет стратегий, соответствующих выбранным фильтрам.' : 'Начните с создания вашей первой торговой стратегии.' }}
        </p>
        <div class="mt-6">
          <button
            v-if="!hasFilters"
            @click="showCreateModal = true"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            <Plus class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            Создать стратегию
          </button>
          <button
            v-else
            @click="clearFilters"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Сбросить фильтры
          </button>
        </div>
      </div>

      <!-- Список стратегий -->
      <TransitionGroup
        v-else
        name="list"
        tag="div"
        class="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
      >
        <div
          v-for="strategy in filteredStrategies"
          :key="strategy.id"
          class="bg-white rounded-lg shadow overflow-hidden"
        >
          <div class="p-6">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-medium text-gray-900">{{ strategy.name }}</h3>
                <p class="text-sm text-gray-500">{{ strategy.symbol }}</p>
              </div>
              <span
                :class="[
                  strategy.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
                  'inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium'
                ]"
              >
                {{ strategy.isActive ? 'Активна' : 'Неактивна' }}
              </span>
            </div>

            <!-- Метрики -->
            <div class="mt-4 grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">Take Profit</p>
                <p class="mt-1 text-sm font-medium text-gray-900">{{ strategy.takeProfit }}%</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Stop Loss</p>
                <p class="mt-1 text-sm font-medium text-gray-900">{{ strategy.stopLoss }}%</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Win Rate</p>
                <p class="mt-1 text-sm font-medium text-gray-900">
                  {{ formatPercent(getStrategyStats(strategy.id).winRate) }}
                </p>
              </div>
              <div>
                <p class="text-sm text-gray-500">P&L (30д)</p>
                <p
                  class="mt-1 text-sm font-medium"
                  :class="getStrategyStats(strategy.id).monthlyPnl >= 0 ? 'text-green-600' : 'text-red-600'"
                >
                  {{ formatMoney(getStrategyStats(strategy.id).monthlyPnl) }}
                </p>
              </div>
            </div>

            <!-- Действия -->
            <div class="mt-6 flex space-x-3">
              <button
                @click="showStrategyStats(strategy)"
                class="flex-1 inline-flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <BarChart2 class="-ml-1 mr-2 h-5 w-5 text-gray-400" />
                Статистика
              </button>
              <Menu as="div" class="relative inline-block text-left">
                <MenuButton class="inline-flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  <MoreVertical class="h-5 w-5" />
                </MenuButton>
                <MenuItems class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
                  <div class="py-1">
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="editStrategy(strategy)"
                        :class="[
                          active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                          'group flex items-center px-4 py-2 text-sm w-full'
                        ]"
                      >
                        <Pencil class="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" />
                        Редактировать
                      </button>
                    </MenuItem>
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="toggleStrategy(strategy)"
                        :class="[
                          active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                          'group flex items-center px-4 py-2 text-sm w-full'
                        ]"
                      >
                        <component
                          :is="strategy.isActive ? Pause : Play"
                          class="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500"
                        />
                        {{ strategy.isActive ? 'Остановить' : 'Запустить' }}
                      </button>
                    </MenuItem>
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="duplicateStrategy(strategy)"
                        :class="[
                          active ? 'bg-gray-100 text-gray-900' : 'text-gray-700',
                          'group flex items-center px-4 py-2 text-sm w-full'
                        ]"
                      >
                        <Copy class="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" />
                        Дублировать
                      </button>
                    </MenuItem>
                    <div class="border-t border-gray-100">
                      <MenuItem v-slot="{ active }">
                        <button
                          @click="deleteStrategy(strategy)"
                          :class="[
                            active ? 'bg-gray-100 text-red-900' : 'text-red-700',
                            'group flex items-center px-4 py-2 text-sm w-full'
                          ]"
                        >
                          <Trash2 class="mr-3 h-5 w-5 text-red-400 group-hover:text-red-500" />
                          Удалить
                        </button>
                      </MenuItem>
                    </div>
                  </div>
                </MenuItems>
              </Menu>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </template>

    <!-- Модальные окна -->
    <StrategyFormModal
      v-if="showCreateModal || editingStrategy"
      :strategy="editingStrategy"
      @close="closeModal"
      @save="saveStrategy"
    />

    <StrategyStats
      v-if="selectedStrategy"
      :strategy="selectedStrategy"
      :stats="getStrategyStats(selectedStrategy.id)"
      :pnl-history="getStrategyPnlHistory(selectedStrategy.id)"
      :recent-trades="getStrategyRecentTrades(selectedStrategy.id)"
      @close="selectedStrategy = null"
    />

    <ExportDialog
      v-if="showExportDialog"
      :data="strategies"
      :fields="strategyFields"
      @close="showExportDialog = false"
      @error="handleExportError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  Plus,
  Lightbulb,
  BarChart2,
  MoreVertical,
  Pencil,
  Play,
  Pause,
  Copy,
  Trash2
} from 'lucide-vue-next'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { useTradingStore } from '@/stores/trading'
import type { Strategy } from '@/types/trading'
import StrategyFilters from '@/components/strategy/StrategyFilters.vue'
import StrategyFormModal from '@/components/strategy/StrategyFormModal.vue'
import StrategyStats from '@/components/strategy/StrategyStats.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import { formatMoney, formatPercent, formatDate } from '@/utils/formatters'
import ExportDialog from '@/components/ui/ExportDialog.vue'
import { useNotificationStore } from '@/stores/notification'

const tradingStore = useTradingStore()
const showCreateModal = ref(false)
const editingStrategy = ref<Strategy | null>(null)
const selectedStrategy = ref<Strategy | null>(null)
const isLoading = ref(false)
const showExportDialog = ref(false)
const error = ref<string | null>(null)

const filters = ref({
  search: '',
  status: '',
  symbols: [],
  takeProfitMin: null,
  takeProfitMax: null,
  stopLossMin: null,
  stopLossMax: null,
  winRateMin: null,
  winRateMax: null
})

const notificationStore = useNotificationStore()

const strategies = computed(() => tradingStore.strategies || [])

const hasFilters = computed(() => {
  return Object.values(filters.value).some(value => {
    if (Array.isArray(value)) return value.length > 0
    return value !== null && value !== ''
  })
})

const filteredStrategies = computed(() => {
  let result = strategies.value

  // Применяем фильтры
  if (filters.value.search) {
    const searchLower = filters.value.search.toLowerCase()
    result = result.filter(s =>
      s.name.toLowerCase().includes(searchLower) ||
      s.symbol.toLowerCase().includes(searchLower)
    )
  }

  if (filters.value.status) {
    result = result.filter(s =>
      filters.value.status === 'active' ? s.isActive : !s.isActive
    )
  }

  if (filters.value.symbols.length > 0) {
    result = result.filter(s => filters.value.symbols.includes(s.symbol))
  }

  // Применяем числовые фильтры
  if (filters.value.takeProfitMin !== null) {
    result = result.filter(s => s.takeProfit >= filters.value.takeProfitMin)
  }
  if (filters.value.takeProfitMax !== null) {
    result = result.filter(s => s.takeProfit <= filters.value.takeProfitMax)
  }

  // ... аналогично для остальных числовых фильтров

  return result
})

const hasStrategies = computed(() => filteredStrategies.value.length > 0)

async function fetchData() {
  isLoading.value = true
  error.value = null
  try {
    await tradingStore.fetchStrategies()
  } catch (err) {
    error.value = 'Не удалось загрузить данные. Пожалуйста, попробуйте позже.'
    console.error('Failed to fetch strategies:', err)
  } finally {
    isLoading.value = false
  }
}

function getStrategyStats(strategyId: number) {
  // Получаем статистику по стратегии
  return {
    winRate: 68,  // Заглушка, должно приходить из store
    monthlyPnl: 1250,
    totalTrades: 45,
    avgPnl: 27.8,
    drawdown: 12.5
  }
}

function getStrategyPnlHistory(strategyId: number) {
  // Заглушка для истории P&L
  return []
}

function getStrategyRecentTrades(strategyId: number) {
  // Заглушка для последних сделок
  return []
}

function clearFilters() {
  filters.value = {
    search: '',
    status: '',
    symbols: [],
    takeProfitMin: null,
    takeProfitMax: null,
    stopLossMin: null,
    stopLossMax: null,
    winRateMin: null,
    winRateMax: null
  }
}

function handleExport() {
  showExportDialog.value = true
}

function handleExportError(error: Error) {
  notificationStore.showError(`Ошибка при экспорте: ${error.message}`)
}

// Добавить конфигурацию полей
const strategyFields = [
  { key: 'name', label: 'Название' },
  { key: 'symbol', label: 'Символ' },
  { key: 'isActive', label: 'Статус', format: (v: boolean) => v ? 'Активна' : 'Неактивна' },
  { key: 'takeProfit', label: 'Take Profit', format: formatPercent },
  { key: 'stopLoss', label: 'Stop Loss', format: formatPercent },
  { key: 'winRate', label: 'Win Rate', format: formatPercent },
  { key: 'totalTrades', label: 'Всего сделок' },
  { key: 'avgPnl', label: 'Средний P&L', format: formatMoney },
  { key: 'createdAt', label: 'Создана', format: formatDate },
  { key: 'updatedAt', label: 'Обновлена', format: formatDate }
]

// Методы для работы с модальным окном создания/редактирования
function closeModal() {
  showCreateModal.value = false
  editingStrategy.value = null
}

async function saveStrategy(strategy: Strategy) {
  try {
    if (strategy.id) {
      // Редактирование существующей стратегии
      await tradingStore.updateStrategy(strategy)
      notificationStore.showSuccess('Стратегия успешно обновлена')
    } else {
      // Создание новой стратегии
      await tradingStore.createStrategy(strategy)
      notificationStore.showSuccess('Стратегия успешно создана')
    }
    closeModal()
    await fetchData()
  } catch (err) {
    console.error('Failed to save strategy:', err)
    notificationStore.showError('Ошибка при сохранении стратегии')
  }
}

// Методы для управления стратегиями
function editStrategy(strategy: Strategy) {
  editingStrategy.value = { ...strategy }
}

async function toggleStrategy(strategy: Strategy) {
  try {
    await tradingStore.updateStrategy({
      ...strategy,
      isActive: !strategy.isActive
    })
    await fetchData()
    notificationStore.showSuccess(
      strategy.isActive ? 'Стратегия остановлена' : 'Стратегия запущена'
    )
  } catch (err) {
    console.error('Failed to toggle strategy:', err)
    notificationStore.showError('Ошибка при изменении статуса стратегии')
  }
}

async function duplicateStrategy(strategy: Strategy) {
  try {
    const { id, createdAt, updatedAt, ...strategyData } = strategy
    await tradingStore.createStrategy({
      ...strategyData,
      name: `${strategy.name} (копия)`,
      isActive: false
    })
    await fetchData()
    notificationStore.showSuccess('Стратегия успешно скопирована')
  } catch (err) {
    console.error('Failed to duplicate strategy:', err)
    notificationStore.showError('Ошибка при копировании стратегии')
  }
}

async function deleteStrategy(strategy: Strategy) {
  if (!confirm('Вы уверены, что хотите удалить эту стратегию?')) {
    return
  }

  try {
    await tradingStore.deleteStrategy(strategy.id)
    await fetchData()
    notificationStore.showSuccess('Стратегия успешно удалена')
  } catch (err) {
    console.error('Failed to delete strategy:', err)
    notificationStore.showError('Ошибка при удалении стратегии')
  }
}

function showStrategyStats(strategy: Strategy) {
  selectedStrategy.value = strategy
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
</style>