// components/FormInput.vue
<template>
  <div>
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
    </label>
    <div class="relative">
      <input
        :id="id"
        v-model="inputValue"
        :type="type"
        :name="name"
        :placeholder="placeholder"
        :class="[
          'block w-full rounded-md shadow-sm',
          error
            ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
            : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500'
        ]"
        v-bind="$attrs"
      />
      <div v-if="error" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
        <ExclamationCircleIcon class="h-5 w-5 text-red-500" />
      </div>
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ExclamationCircleIcon } from '@heroicons/vue/24/outline'
import { useField } from 'vee-validate'

const props = defineProps<{
  name: string
  label?: string
  modelValue?: string | number
  type?: string
  placeholder?: string
  rules?: string | Record<string, any>
}>()

const emit = defineEmits(['update:modelValue'])

const id = computed(() => `field-${props.name}`)

const { value: inputValue, errorMessage: error } = useField(props.name, props.rules, {
  initialValue: props.modelValue
})
</script>