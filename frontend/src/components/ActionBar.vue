<script setup lang="ts"></script>

<template>
  <div
    class="relative flex flex-col gap-4 overflow-hidden rounded-2xl border border-accent bg-linear-to-br from-accent/40 via-surface to-primary/20 p-6 shadow-sm sm:flex-row sm:items-center sm:justify-between"
  >
    <div class="absolute -top-12 -right-12 h-36 w-36 rounded-full bg-accent/40 blur-3xl"></div>
    <slot name="default"></slot>
  </div>
</template>

<style scoped></style>
