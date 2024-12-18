<template>
  <div class="min-h-full">
    <div class="fixed inset-y-0 flex w-64 flex-col">
      <!-- Sidebar component -->
      <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-primary-600 px-6">
        <div class="flex h-16 shrink-0 items-center">
          <h1 class="text-2xl font-bold text-white">Trading Bot</h1>
        </div>

        <nav class="flex flex-1 flex-col">
          <ul role="list" class="flex flex-1 flex-col gap-y-7">
            <!-- Основное меню -->
            <li>
              <ul role="list" class="-mx-2 space-y-1">
                <li v-for="item in navigation" :key="item.name">
                  <router-link
                    :to="item.href"
                    :class="[
                      item.current ? 'bg-primary-700 text-white' : 'text-primary-200 hover:text-white hover:bg-primary-700',
                      'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold'
                    ]"
                  >
                    <component :is="item.icon" class="h-6 w-6 shrink-0" :class="item.current ? 'text-white' : 'text-primary-200 group-hover:text-white'" />
                    {{ item.name }}
                  </router-link>
                </li>
              </ul>
            </li>

            <!-- Профиль пользователя -->
            <li class="mt-auto">
              <Menu as="div" class="relative">
                <MenuButton class="flex items-center gap-x-4 py-3 text-sm font-semibold leading-6 text-white">
                  <span class="sr-only">Меню пользователя</span>
                  <UserCircle class="h-8 w-8 rounded-full text-primary-200" />
                  <span class="flex items-center">
                    <span>{{ userFullName }}</span>
                    <ChevronUp class="ml-2 h-5 w-5 text-primary-200" />
                  </span>
                </MenuButton>
                <transition
                  enter-active-class="transition ease-out duration-100"
                  enter-from-class="transform opacity-0 scale-95"
                  enter-to-class="transform opacity-100 scale-100"
                  leave-active-class="transition ease-in duration-75"
                  leave-from-class="transform opacity-100 scale-100"
                  leave-to-class="transform opacity-0 scale-95"
                >
                  <MenuItems class="absolute bottom-full left-0 mb-2 w-56 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div class="py-1">
                      <MenuItem v-slot="{ active }">
                        <router-link to="/profile" :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']">
                          Профиль
                        </router-link>
                      </MenuItem>
                      <MenuItem v-slot="{ active }">
                        <button
                          @click="logout"
                          :class="[active ? 'bg-gray-100' : '', 'block w-full px-4 py-2 text-left text-sm text-red-700']"
                        >
                          Выйти
                        </button>
                      </MenuItem>
                    </div>
                  </MenuItems>
                </transition>
              </Menu>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Main content -->
    <div class="pl-64">
      <main class="py-10">
        <div class="px-4 sm:px-6 lg:px-8">
          <router-view></router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { useAuthStore } from '@/stores/auth'
import {
  Home,
  BarChart2,
  DollarSign,
  LayoutGrid,
  UserCircle,
  ChevronUp
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userFullName = computed(() => authStore.userFullName)

const navigation = computed(() => [
  {
    name: 'Dashboard',
    href: '/',
    icon: Home,
    current: route.path === '/'
  },
  {
    name: 'Strategies',
    href: '/strategies',
    icon: BarChart2,
    current: route.path === '/strategies'
  },
  {
    name: 'Trades',
    href: '/trades',
    icon: DollarSign,
    current: route.path === '/trades'
  },
  {
    name: 'Positions',
    href: '/positions',
    icon: LayoutGrid,
    current: route.path === '/positions'
  },
  // Добавляем профиль
  {
    name: 'Profile',
    href: '/profile',
    icon: UserCircle,
    current: route.path === '/profile'
  }
])

async function logout() {
  await authStore.logout()
  router.push('/auth/login')
}
</script>