<script setup lang="ts">
import { onMounted, ref } from 'vue'
import api from '@/services/api.ts'
import { getAccessToken } from '@/utils/LocalStorageUtils.ts'
import router from '@/router'
import type { User } from '@/types/user.ts'

interface AccountDetails extends User {
  email: string
}

const user = ref<AccountDetails>()
const getMe = async () => {
  const token = getAccessToken()
  if (!token) {
    router.push({ name: 'Login' })
  }
  try {
    const response = await api.get('/users/me')

    user.value = response.data
  } catch (err) {
    console.error(err)
  }
}

onMounted(async () => {
  await getMe()
})
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background p-6">
    <div class="w-full max-w-xl rounded-2xl border border-border bg-surface p-6 shadow-sm">
      <div class="mb-6 flex items-center gap-4">
        <img
          :src="user?.image_file"
          alt="Client profile"
          class="h-28 w-28 rounded-full object-cover ring-2 ring-border"
        />

        <div>
          <p class="text-lg font-bold uppercase tracking-[0.2em] text-foreground underline underline-offset-4 text-shadow-2xs text-shadow-accent ">
            {{ user?.username ?? 'Username' }}
          </p>
        </div>
      </div>

      <ul class="space-y-3">
        <li
          class="flex items-center justify-between rounded-xl border border-border bg-white px-4 py-3"
        >
          <span class="text-sm font-medium text-foreground/60">Email</span>
          <span class="text-sm font-semibold text-foreground">{{
            user?.email ?? 'email@exemple.com'
          }}</span>
        </li>

        <li
          class="flex items-center justify-between rounded-xl border border-border bg-white px-4 py-3"
        >
          <span class="text-sm font-medium text-foreground/60">Created at</span>
          <span class="text-sm font-semibold text-foreground">2024-01-15T10:42:00Z</span>
        </li>
      </ul>
      <div>
        <button class="mt-3 p-4 border ">Edit</button>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
