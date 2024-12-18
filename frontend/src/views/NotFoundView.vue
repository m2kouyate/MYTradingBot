<!-- views/NotFoundView.vue -->
<template>
  <div class="flex flex-col items-center justify-center min-h-screen py-12 bg-white">
    <h1 class="text-9xl font-bold text-gray-900">404</h1>
    <p class="mt-4 text-xl text-gray-600">Страница не найдена</p>
    <router-link
      to="/"
      class="mt-8 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
    >
      Вернуться на главную
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  console.log('404 route mounted')
})
</script>