<!-- components/market/DataSourceSelector.vue -->
<template>
  <div class="bg-white shadow rounded-lg divide-y divide-gray-200">
    <!-- Заголовок -->
    <div class="p-4 sm:p-6">
      <h3 class="text-lg font-medium text-gray-900">Источники данных</h3>
      <p class="mt-1 text-sm text-gray-500">
        Настройте источники данных для бэктестинга
      </p>
    </div>

    <!-- Список источников -->
    <div class="px-4 py-5 sm:p-6">
      <div class="space-y-4">
        <div v-for="source in dataSources" :key="source.id" class="relative">
          <!-- Основные настройки -->
          <div class="flex items-start">
            <div class="flex items-center h-5">
              <input
                :id="source.id"
                v-model="selectedSources[source.id].enabled"
                type="checkbox"
                class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
            </div>
            <div class="ml-3 flex-grow">
              <label :for="source.id" class="font-medium text-gray-700">
                {{ source.name }}
              </label>
              <p class="text-sm text-gray-500">{{ source.description }}</p>
            </div>
            <button
              v-if="selectedSources[source.id].enabled"
              @click="openSourceSettings(source)"
              type="button"
              class="ml-3 text-gray-400 hover:text-gray-500"
            >
              <CogIcon class="h-5 w-5" />
            </button>
          </div>

          <!-- Детали источника -->
          <div
            v-if="selectedSources[source.id].enabled"
            class="mt-2 ml-7 text-sm"
          >
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-gray-500">Поддерживаемые активы:</p>
                <div class="mt-1 flex gap-2">
                  <span
                    v-for="asset in source.supportedAssets"
                    :key="asset"
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                    :class="getAssetBadgeClass(asset)"
                  >
                    {{ formatAssetType(asset) }}
                  </span>
                </div>
              </div>
              <div>
                <p class="text-gray-500">Таймфреймы:</p>
                <div class="mt-1 flex flex-wrap gap-1">
                  <span
                    v-for="tf in source.supportedTimeframes"
                    :key="tf"
                    class="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-gray-800 text-xs font-medium"
                  >
                    {{ tf }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Настройки приоритетов -->
    <div class="px-4 py-5 sm:p-6" v-if="hasMultipleEnabled">
      <h4 class="text-sm font-medium text-gray-900">Приоритет источников</h4>
      <p class="mt-1 text-sm text-gray-500">
        Перетащите источники для изменения приоритета
      </p>
      <draggable
        v-model="priorityList"
        class="mt-3 space-y-2"
        :item-key="source => source.id"
        handle=".handle"
      >
        <template #item="{ element: source }">
          <div
            v-if="selectedSources[source.id].enabled"
            class="flex items-center p-2 bg-gray-50 rounded-lg"
          >
            <BarsArrowUpIcon class="handle h-5 w-5 text-gray-400 cursor-move" />
            <span class="ml-2 text-sm text-gray-900">{{ source.name }}</span>
          </div>
        </template>
      </draggable>
    </div>
  </div>

  <!-- Модальное окно настроек -->
  <TransitionRoot show={showSettings} as="template">
    <Dialog
      as="div"
      class="relative z-10"
      @close="showSettings = false"
    >
      <TransitionChild
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel class="relative transform rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div v-if="selectedSource">
                <div class="sm:flex sm:items-start">
                  <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                    <DialogTitle as="h3" class="text-lg font-semibold leading-6 text-gray-900">
                      Настройки {{ selectedSource.name }}
                    </DialogTitle>

                    <div class="mt-4 space-y-4">
                      <!-- API Key -->
                      <div v-if="selectedSource.requiresApiKey">
                        <label class="block text-sm font-medium text-gray-700">
                          API Key
                        </label>
                        <input
                          type="password"
                          v-model="sourceSettings.apiKey"
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                        />
                      </div>

                      <!-- Пользовательский endpoint -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700">
                          Пользовательский endpoint
                        </label>
                        <input
                          type="text"
                          v-model="sourceSettings.customEndpoint"
                          placeholder="Опционально"
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                        />
                      </div>

                      <!-- Кэширование -->
                      <div class="flex items-start">
                        <div class="flex items-center h-5">
                          <input
                            type="checkbox"
                            v-model="sourceSettings.useCache"
                            class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                          />
                        </div>
                        <div class="ml-3">
                          <label class="text-sm font-medium text-gray-700">
                            Использовать кэширование
                          </label>
                          <p class="text-sm text-gray-500">
                            Кэшировать исторические данные для быстрого доступа
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Действия -->
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 sm:col-start-2"
                    @click="saveSettings"
                  >
                    Сохранить
                  </button>
                  <button
                    type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    @click="showSettings = false"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { CogIcon, BarsArrowUpIcon } from '@heroicons/vue/24/outline'
import draggable from 'vuedraggable'
import type { DataSource, DataSourceInfo, DataSourceConfig } from '@/types/market'
import { useNotificationStore } from '@/stores/notification'

const props = defineProps<{
  modelValue: Record<DataSource, DataSourceConfig>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<DataSource, DataSourceConfig>]
  'change': [source: DataSource, config: DataSourceConfig]
}>()

const notificationStore = useNotificationStore()

// Информация об источниках данных
const dataSources: DataSourceInfo[] = [
  {
    id: 'BINANCE',
    name: 'Binance',
    description: 'Криптовалютная биржа с большим объемом торгов',
    supportedTimeframes: ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'],
    supportedAssets: ['crypto'],
    requiresApiKey: false,
    rateLimit: {
      requestsPerMinute: 1200,
      requestsPerDay: 100000
    }
  },
  {
    id: 'YAHOO',
    name: 'Yahoo Finance',
    description: 'Исторические данные для акций, ETF и индексов',
    supportedTimeframes: ['1d', '1w'],
    supportedAssets: ['stocks'],
    requiresApiKey: false,
    rateLimit: {
      requestsPerMinute: 100,
      requestsPerDay: 10000
    }
  },
  {
    id: 'POLYGON',
    name: 'Polygon.io',
    description: 'Профессиональные рыночные данные для всех типов активов',
    supportedTimeframes: ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'],
    supportedAssets: ['stocks', 'crypto', 'forex'],
    requiresApiKey: true,
    rateLimit: {
      requestsPerMinute: 500,
      requestsPerDay: 50000
    }
  }
]

// Состояние
const selectedSources = ref<Record<DataSource, DataSourceConfig>>(props.modelValue)
const showSettings = ref(false)
const selectedSource = ref<DataSourceInfo | null>(null)
const sourceSettings = ref<DataSourceConfig>({
  enabled: false,
  priority: 0,
  useCache: true
})
const validationErrors = ref<Record<string, string[]>>({})

// Приоритеты источников
const priorityList = computed(() => {
  return dataSources
    .filter(source => selectedSources.value[source.id].enabled)
    .sort((a, b) =>
      selectedSources.value[a.id].priority - selectedSources.value[b.id].priority
    )
})

const hasMultipleEnabled = computed(() => {
  return Object.values(selectedSources.value)
    .filter(config => config.enabled)
    .length > 1
})

// Методы
function openSourceSettings(source: DataSourceInfo) {
  selectedSource.value = source
  sourceSettings.value = { ...selectedSources.value[source.id] }
  showSettings.value = true
}

function saveSettings() {
  if (!selectedSource.value) return

  // Валидация API ключа
  if (selectedSource.value.requiresApiKey && !sourceSettings.value.apiKey) {
    notificationStore.showError('API ключ обязателен для этого источника')
    return
  }

  // Валидация endpoint
  if (sourceSettings.value.customEndpoint && !isValidUrl(sourceSettings.value.customEndpoint)) {
    notificationStore.showError('Некорректный URL для endpoint')
    return
  }

  selectedSources.value[selectedSource.value.id] = {
    ...sourceSettings.value
  }

  emit('update:modelValue', selectedSources.value)
  emit('change', selectedSource.value.id, sourceSettings.value)
  showSettings.value = false
}

function updatePriorities() {
  priorityList.value.forEach((source, index) => {
    selectedSources.value[source.id].priority = index
  })
  emit('update:modelValue', selectedSources.value)
}

// Вспомогательные функции
function getAssetBadgeClass(asset: 'crypto' | 'stocks' | 'forex'): string {
  switch (asset) {
    case 'crypto':
      return 'bg-blue-100 text-blue-800'
    case 'stocks':
      return 'bg-green-100 text-green-800'
    case 'forex':
      return 'bg-purple-100 text-purple-800'
  }
}

function formatAssetType(asset: string): string {
  const labels = {
    crypto: 'Криптовалюты',
    stocks: 'Акции',
    forex: 'Форекс'
  }
  return labels[asset as keyof typeof labels] || asset
}

function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// Наблюдатели
watch(priorityList, updatePriorities)

watch(() => props.modelValue, (newValue) => {
  selectedSources.value = { ...newValue }
}, { deep: true })
</script>

<style scoped>
.handle {
  cursor: move;
}

.sortable-ghost {
  opacity: 0.5;
}

.sortable-chosen {
  background-color: #f3f4f6;
}
</style>
