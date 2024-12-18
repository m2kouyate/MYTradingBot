<!-- components/strategy/StrategyFilters.vue -->
<template>
  <div class="bg-white shadow rounded-lg p-4 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- Поиск -->
      <div class="relative">
        <input
          type="text"
          v-model="localFilters.search"
          placeholder="Поиск по названию или символу"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm pl-10"
        />
        <MagnifyingGlassIcon class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
      </div>

      <!-- Статус -->
      <div>
        <select
          v-model="localFilters.status"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="">Все статусы</option>
          <option value="active">Активные</option>
          <option value="inactive">Неактивные</option>
        </select>
      </div>

      <!-- Символы -->
      <div>
        <Combobox v-model="localFilters.symbols" multiple>
          <div class="relative">
            <ComboboxInput
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              placeholder="Выберите символы"
              @change="querySymbols = $event.target.value"
              :displayValue="(symbols: string[]) => symbols.join(', ')"
            />
            <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon class="h-5 w-5 text-gray-400" />
            </ComboboxButton>

            <Transition
              enter-active-class="transition duration-100 ease-out"
              enter-from-class="transform scale-95 opacity-0"
              enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-75 ease-in"
              leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0"
            >
              <ComboboxOptions class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                <ComboboxOption
                  v-for="symbol in availableSymbols"
                  :key="symbol"
                  :value="symbol"
                  v-slot="{ selected, active }"
                >
                  <li
                    :class="[
                      'relative cursor-default select-none py-2 pl-10 pr-4',
                      active ? 'bg-primary-600 text-white' : 'text-gray-900'
                    ]"
                  >
                    <span :class="[selected ? 'font-medium' : 'font-normal']">
                      {{ symbol }}
                    </span>
                    <span
                      v-if="selected"
                      :class="[
                        active ? 'text-white' : 'text-primary-600',
                        'absolute inset-y-0 left-0 flex items-center pl-3'
                      ]"
                    >
                      <CheckIcon class="h-5 w-5" />
                    </span>
                  </li>
                </ComboboxOption>
              </ComboboxOptions>
            </Transition>
          </div>
        </Combobox>
      </div>

      <!-- Доп. фильтры -->
      <div class="relative">
        <Menu>
          <MenuButton class="inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
            Дополнительные фильтры
            <ChevronDownIcon class="-mr-1 ml-2 h-5 w-5" />
          </MenuButton>

          <MenuItems class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
            <div class="py-1">
              <div class="px-3 py-2">
                <label class="text-sm font-medium text-gray-700">Take Profit (%)</label>
                <div class="mt-1 flex space-x-2">
                  <input
                    type="number"
                    v-model="localFilters.takeProfitMin"
                    placeholder="От"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                  <input
                    type="number"
                    v-model="localFilters.takeProfitMax"
                    placeholder="До"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                </div>
              </div>
              <div class="px-3 py-2">
                <label class="text-sm font-medium text-gray-700">Stop Loss (%)</label>
                <div class="mt-1 flex space-x-2">
                  <input
                    type="number"
                    v-model="localFilters.stopLossMin"
                    placeholder="От"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                  <input
                    type="number"
                    v-model="localFilters.stopLossMax"
                    placeholder="До"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                </div>
              </div>
              <div class="px-3 py-2">
                <label class="text-sm font-medium text-gray-700">Win Rate (%)</label>
                <div class="mt-1 flex space-x-2">
                  <input
                    type="number"
                    v-model="localFilters.winRateMin"
                    placeholder="От"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                  <input
                    type="number"
                    v-model="localFilters.winRateMax"
                    placeholder="До"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>
          </MenuItems>
        </Menu>
      </div>
    </div>

    <!-- Активные фильтры -->
    <div v-if="hasActiveFilters" class="mt-4 flex flex-wrap gap-2">
      <span
        v-for="filter in activeFiltersList"
        :key="filter.key"
        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
      >
        {{ filter.label }}
        <button
          type="button"
          @click="clearFilter(filter.key)"
          class="ml-1 inline-flex items-center p-0.5 text-primary-400 hover:bg-primary-200 hover:text-primary-500"
        >
          <XMarkIcon class="h-3 w-3" />
        </button>
      </span>
      <button
        v-if="hasActiveFilters"
        @click="clearAllFilters"
        class="text-xs text-gray-500 hover:text-gray-700"
      >
        Очистить все фильтры
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Combobox, ComboboxButton, ComboboxInput, ComboboxOptions, ComboboxOption } from '@headlessui/vue'
import { MagnifyingGlassIcon, ChevronDownIcon, ChevronUpDownIcon, CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { Menu, MenuButton, MenuItems } from '@headlessui/vue'
import { useTradingStore } from '@/stores/trading'

const tradingStore = useTradingStore()

interface Filters {
  search: string
  status: string
  symbols: string[]
  takeProfitMin: number | null
  takeProfitMax: number | null
  stopLossMin: number | null
  stopLossMax: number | null
  winRateMin: number | null
  winRateMax: number | null
}

const props = defineProps<{
  filters: Filters
}>()

const emit = defineEmits<{
  (e: 'update:filters', filters: Filters): void
}>()

const querySymbols = ref('')
const localFilters = ref<Filters>({ ...props.filters })

// Available symbols from store
const availableSymbols = computed(() =>
  Array.from(new Set(tradingStore.strategies?.map(s => s.symbol) || ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']))
)

// Watch for props changes
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

// Watch for local changes and emit updates
watch(localFilters, (newFilters) => {
  emit('update:filters', { ...newFilters })
}, { deep: true })

const hasActiveFilters = computed(() => {
  return localFilters.value.search !== '' ||
    localFilters.value.status !== '' ||
    localFilters.value.symbols.length > 0 ||
    localFilters.value.takeProfitMin != null ||
    localFilters.value.takeProfitMax != null ||
    localFilters.value.stopLossMin != null ||
    localFilters.value.stopLossMax != null ||
    localFilters.value.winRateMin != null ||
    localFilters.value.winRateMax != null
})

const activeFiltersList = computed(() => {
  const list = []

  if (localFilters.value.search) {
    list.push({ key: 'search', label: `Поиск: ${localFilters.value.search}` })
  }

  if (localFilters.value.status) {
    list.push({ key: 'status', label: localFilters.value.status === 'active' ? 'Активные' : 'Неактивные' })
  }

  if (localFilters.value.symbols.length > 0) {
    list.push({ key: 'symbols', label: `Символы: ${localFilters.value.symbols.join(', ')}` })
  }

  if (localFilters.value.takeProfitMin != null || localFilters.value.takeProfitMax != null) {
    list.push({ key: 'takeProfit', label: `Take Profit: ${localFilters.value.takeProfitMin || 0} - ${localFilters.value.takeProfitMax || '∞'}%` })
  }

  if (localFilters.value.stopLossMin != null || localFilters.value.stopLossMax != null) {
    list.push({ key: 'stopLoss', label: `Stop Loss: ${localFilters.value.stopLossMin || 0} - ${localFilters.value.stopLossMax || '∞'}%` })
  }

  if (localFilters.value.winRateMin != null || localFilters.value.winRateMax != null) {
    list.push({ key: 'winRate', label: `Win Rate: ${localFilters.value.winRateMin || 0} - ${localFilters.value.winRateMax || '∞'}%` })
  }

  return list
})

function clearFilter(key: string) {
  if (key === 'symbols') {
    localFilters.value.symbols = []
  } else if (key === 'takeProfit') {
    localFilters.value.takeProfitMin = null
    localFilters.value.takeProfitMax = null
  } else if (key === 'stopLoss') {
    localFilters.value.stopLossMin = null
    localFilters.value.stopLossMax = null
  } else if (key === 'winRate') {
    localFilters.value.winRateMin = null
    localFilters.value.winRateMax = null
  } else {
    (localFilters.value[key as keyof Filters] as any) = ''
  }
}

function clearAllFilters() {
  localFilters.value = {
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
</script>