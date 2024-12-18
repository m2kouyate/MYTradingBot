<template>
  <div class="relative">
    <!-- Мобильное меню -->
    <div class="lg:hidden">
      <button
        @click="isOpen = !isOpen"
        class="fixed top-4 left-4 z-40 p-2 rounded-md bg-primary-600 text-white"
      >
        <Menu v-if="!isOpen" class="h-6 w-6" />
        <X v-else class="h-6 w-6" />
      </button>

      <!-- Мобильная навигация -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform -translate-x-full"
        enter-to-class="transform translate-x-0"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform translate-x-0"
        leave-to-class="transform -translate-x-full"
      >
        <div v-if="isOpen" class="fixed inset-0 z-30">
          <!-- Затемнение фона -->
          <div class="fixed inset-0 bg-black/30" @click="isOpen = false" />

          <!-- Меню -->
          <nav class="relative w-64 h-full bg-primary-600 text-white overflow-y-auto">
            <div class="p-4">
              <h1 class="text-xl font-bold mb-6">Trading Bot</h1>
              <div class="space-y-2">
                <RouterLink
                  v-for="item in menuItems"
                  :key="item.path"
                  :to="item.path"
                  class="flex items-center px-4 py-2 rounded-md hover:bg-primary-700"
                  :class="{ 'bg-primary-700': currentRoute === item.path }"
                  @click="isOpen = false"
                >
                  <component :is="item.icon" class="h-5 w-5 mr-3" />
                  {{ item.name }}
                </RouterLink>
              </div>
            </div>

            <!-- Профиль пользователя в мобильном меню -->
            <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-primary-700">
              <div class="flex items-center">
                <UserCircle class="h-8 w-8 text-white" />
                <span class="ml-2">{{ username }}</span>
              </div>
            </div>
          </nav>
        </div>
      </Transition>
    </div>

    <!-- Десктопное меню -->
    <nav class="hidden lg:block fixed inset-y-0 left-0 w-64 bg-primary-600 text-white">
      <div class="p-4">
        <h1 class="text-xl font-bold mb-6">Trading Bot</h1>
        <div class="space-y-2">
          <RouterLink
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center px-4 py-2 rounded-md hover:bg-primary-700"
            :class="{ 'bg-primary-700': currentRoute === item.path }"
          >
            <component :is="item.icon" class="h-5 w-5 mr-3" />
            {{ item.name }}
          </RouterLink>
        </div>
      </div>

      <!-- Профиль пользователя в десктопном меню -->
      <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-primary-700">
        <div class="flex items-center">
          <UserCircle class="h-8 w-8 text-white" />
          <span class="ml-2">{{ username }}</span>
        </div>
      </div>
    </nav>

    <!-- Основной контент -->
    <div class="lg:ml-64">
      <main class="p-4">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Menu,
  X,
  LayoutDashboard,
  LineChart,
  Wallet,
  BarChart2,
  UserCircle
} from 'lucide-vue-next'

const route = useRoute()
const authStore = useAuthStore()
const isOpen = ref(false)

const menuItems = [
  {
    name: 'Dashboard',
    path: '/',
    icon: LayoutDashboard
  },
  {
    name: 'Strategies',
    path: '/strategies',
    icon: LineChart
  },
  {
    name: 'Trades',
    path: '/trades',
    icon: BarChart2
  },
  {
    name: 'Positions',
    path: '/positions',
    icon: Wallet
  },
  {
    name: 'Profile',
    path: '/profile',
    icon: UserCircle
  }
]

const currentRoute = computed(() => route.path)
const username = computed(() => authStore.user?.username || '')
</script>