<script setup lang="ts">
import SideBar from '@/components/SideBar.vue'
</script>

<template>
  <div class="flex h-screen">
    <SideBar />
    <main class="flex-1 overflow-y-auto p-8">
      <slot />
    </main>
  </div>
</template>

<style scoped></style>
