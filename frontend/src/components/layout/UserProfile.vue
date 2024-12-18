<!-- components/layout/UserProfile.vue -->
<template>
  <Menu as="div" class="relative ml-3">
    <MenuButton class="flex items-center text-white">
      <span class="sr-only">Открыть меню пользователя</span>
      <UserIcon class="h-8 w-8 rounded-full p-1 bg-primary-700" />
      <span class="ml-2 text-sm">{{ authStore.userFullName }}</span>
    </MenuButton>

    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <MenuItems
        class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
      >
        <MenuItem v-slot="{ active }">
          <a
            href="#"
            @click.prevent="openProfile"
            :class="[
              active ? 'bg-gray-100' : '',
              'block px-4 py-2 text-sm text-gray-700'
            ]"
          >
            Профиль
          </a>
        </MenuItem>
        <MenuItem v-slot="{ active }">
          <a
            href="#"
            @click.prevent="openSettings"
            :class="[
              active ? 'bg-gray-100' : '',
              'block px-4 py-2 text-sm text-gray-700'
            ]"
          >
            Настройки
          </a>
        </MenuItem>
        <MenuItem v-slot="{ active }">
          <a
            href="#"
            @click.prevent="logout"
            :class="[
              active ? 'bg-gray-100' : '',
              'block px-4 py-2 text-sm text-gray-700'
            ]"
          >
            Выйти
          </a>
        </MenuItem>
      </MenuItems>
    </transition>
  </Menu>
</template>

<script setup lang="ts">
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { UserIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

function openProfile() {
  router.push('/profile')
}

function openSettings() {
  router.push('/settings')
}

function logout() {
  authStore.logout()
}
</script>