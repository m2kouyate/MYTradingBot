<!-- views/auth/AuthLayout.vue -->
<template>
  <div class="min-h-screen bg-gray-50">
    <notification-toast />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import NotificationToast from '@/components/NotificationToast.vue'
</script>