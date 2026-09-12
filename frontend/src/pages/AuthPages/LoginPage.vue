<script setup lang="ts">
import DefaultButton from '@/components/DefaultButton.vue'

import api from '@/services/api.ts'
import { ref } from 'vue'
import { setAccessToken } from '@/utils/LocalStorageUtils.ts'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

interface ResponseData {
  access_token: string
  token_type: string
}

const router = useRouter();

const handleSubmit = async () => {
  const formData = new URLSearchParams()
  console.log(email.value)
  formData.append('username', email.value)
  formData.append('password', password.value)
  try {
    isLoading.value = true
    const response = await api.post('/users/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })

    const { access_token, token_type }: ResponseData = response.data
    if (access_token && token_type) {
      setAccessToken(access_token)
      router.push({ name: 'Dashboard' })
    }
  } catch (err) {
    error.value = String(err)
    console.error()
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="grid min-h-full place-items-center">
    <div class="flex bg-sidebar-foreground p-10 rounded-2xl justify-center w-2/3">
      <div class="w-4xl">
        <h1 class="text-2xl font-semibold">Welcome back!</h1>
        <p>For accessing your clients use your email and password to log in into the platform!</p>
      </div>
      <form @submit.prevent="handleSubmit" class="w-full max-w-sm">
        <div>
          <h1 class="text-foreground text-shadow-2xs text-2xl font-bold mb-4">LogIn</h1>
        </div>
        <div class="flex flex-col gap-4">
          <input
            v-model="email"
            placeholder="Email"
            name="email"
            type="email"
            class="w-full border border-border rounded-lg px-4 py-3 text-base"
          />
          <input
            v-model="password"
            placeholder="Password"
            name="password"
            type="password"
            class="w-full border border-border rounded-lg px-4 py-3 text-base"
          />
          <DefaultButton type="submit" :disabled="isLoading">
            {{ isLoading ? 'Loading...' : 'Log in' }}
          </DefaultButton>
        </div>
        <RouterLink
          :to="{ name: 'ForgotPassword' }"
          class="text-primary hover:underline cursor-pointer"
          >Forgot password?</RouterLink
        ><br />
        <RouterLink :to="{ name: 'Signup' }" class="text-primary hover:underline cursor-pointer"
          >You don't have an account?</RouterLink
        >
        <span>{{ error }}</span>
      </form>
    </div>
  </div>
</template>

<style scoped></style>
