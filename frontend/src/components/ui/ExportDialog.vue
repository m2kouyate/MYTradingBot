<!-- components/ui/ExportDialog.vue -->
<template>
  <TransitionRoot appear show as="template">
    <Dialog as="div" @close="close" class="relative z-50">
      <div class="fixed inset-0 bg-black/30" />

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <DialogPanel class="w-full max-w-2xl transform overflow-hidden rounded-lg bg-white p-6 shadow-xl transition-all">
            <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
              Экспорт данных
            </DialogTitle>

            <!-- Настройки экспорта -->
            <div class="mt-4 space-y-4">
              <!-- Формат -->
              <div>
                <label class="text-sm font-medium text-gray-700">Формат файла</label>
                <div class="mt-2 flex space-x-4">
                  <label
                    v-for="format in availableFormats"
                    :key="format.value"
                    class="inline-flex items-center"
                  >
                    <input
                      type="radio"
                      v-model="selectedFormat"
                      :value="format.value"
                      class="form-radio h-4 w-4 text-primary-600 border-gray-300"
                    >
                    <span class="ml-2 text-sm text-gray-700">{{ format.label }}</span>
                  </label>
                </div>
              </div>

              <!-- Выбор полей -->
              <div>
                <label class="text-sm font-medium text-gray-700">Поля для экспорта</label>
                <div class="mt-2 grid grid-cols-2 gap-2">
                  <label
                    v-for="field in availableFields"
                    :key="field.key"
                    class="inline-flex items-center"
                  >
                    <input
                      type="checkbox"
                      v-model="selectedFields"
                      :value="field.key"
                      class="form-checkbox h-4 w-4 text-primary-600 border-gray-300 rounded"
                    >
                    <span class="ml-2 text-sm text-gray-700">{{ field.label }}</span>
                  </label>
                </div>
              </div>

              <!-- Предпросмотр -->
              <div>
                <label class="text-sm font-medium text-gray-700">Предпросмотр</label>
                <div class="mt-2 border rounded-lg overflow-hidden">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th
                          v-for="field in selectedFieldsConfig"
                          :key="field.key"
                          class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          {{ field.label }}
                        </th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="(item, index) in previewData" :key="index">
                        <td
                          v-for="field in selectedFieldsConfig"
                          :key="field.key"
                          class="px-4 py-2 whitespace-nowrap text-sm text-gray-900"
                        >
                          {{ field.format ? field.format(item[field.key]) : item[field.key] }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p class="mt-1 text-xs text-gray-500">
                  Показаны первые 5 записей из {{ totalRecords }}
                </p>
              </div>
            </div>

            <!-- Действия -->
            <div class="mt-6 flex justify-end space-x-3">
              <button
                type="button"
                @click="close"
                class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
              >
                Отмена
              </button>
              <button
                type="button"
                @click="startExport"
                :disabled="!canExport || isExporting"
                class="inline-flex justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 disabled:bg-gray-400"
              >
                <Download
                  v-if="!isExporting"
                  class="mr-2 h-4 w-4"
                />
                <Loader
                  v-else
                  class="animate-spin mr-2 h-4 w-4"
                />
                {{ isExporting ? 'Экспорт...' : 'Экспортировать' }}
              </button>
            </div>
          </DialogPanel>
        </div>
      </div>

      <!-- Прогресс экспорта -->
      <ExportProgress
        v-if="isExporting"
        :progress="exportProgress"
      />
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionRoot
} from '@headlessui/vue'
import {
  Download,
  Loader
} from 'lucide-vue-next'
import { ExportService } from '@/services/exportService'
import ExportProgress from './ExportProgress.vue'

const props = defineProps<{
  data: any[]
  fields: Array<{
    key: string
    label: string
    format?: (value: any) => string
  }>
}>()

const emit = defineEmits<{
  close: []
  error: [error: Error]
}>()

// Состояние
const selectedFormat = ref<'csv' | 'xlsx' | 'pdf'>('csv')
const selectedFields = ref<string[]>([])
const isExporting = ref(false)
const exportProgress = ref(0)

// Вычисляемые свойства
const availableFormats = [
  { value: 'csv', label: 'CSV' },
  { value: 'xlsx', label: 'Excel' },
  { value: 'pdf', label: 'PDF' }
]

const availableFields = computed(() => props.fields)

const selectedFieldsConfig = computed(() =>
  props.fields.filter(field => selectedFields.value.includes(field.key))
)

const previewData = computed(() =>
  props.data.slice(0, 5)
)

const totalRecords = computed(() => props.data.length)

const canExport = computed(() =>
  selectedFields.value.length > 0 && selectedFormat.value
)

// Методы
async function startExport() {
  try {
    isExporting.value = true
    exportProgress.value = 0

    // Фильтруем данные по выбранным полям
    const filteredData = props.data.map(item => {
      const filtered: Record<string, any> = {}
      selectedFields.value.forEach(field => {
        filtered[field] = item[field]
      })
      return filtered
    })

    // Экспортируем с выбранными полями
    await ExportService.exportData(filteredData, {
      filename: `export_${Date.now()}`,
      format: selectedFormat.value,
      columns: selectedFieldsConfig.value,
      onProgress: (progress) => {
        exportProgress.value = progress
      }
    })

    close()
  } catch (error) {
    emit('error', error as Error)
  } finally {
    isExporting.value = false
  }
}

function close() {
  emit('close')
}

// Инициализация
selectedFields.value = props.fields.map(f => f.key)
</script>