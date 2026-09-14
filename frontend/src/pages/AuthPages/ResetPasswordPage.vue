<script setup lang="ts">
import { ref } from 'vue'
import DefaultButton from '@/components/DefaultButton.vue'
import api from '@/services/api.ts'
import { useRoute } from 'vue-router'
import router from '@/router'

const password = ref('')
const confirmPassword = ref('')
const submitted = ref(false)
const error = ref<string[]>([])

const SPECIAL_CHARS = /[!"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]/
const upperCaseChars = /[A-Z]/

const route = useRoute()

const handleSubmit = async () => {
  error.value = []
  submitted.value = false

  if (!password.value || !confirmPassword.value) {
    error.value.push('Please fill in both password fields.')
    return
  }

  if (password.value.length <= 8) {
    error.value.push('Password should contain 8 or more characters.')
  }

  if (!SPECIAL_CHARS.test(password.value)) {
    error.value.push('Password must contain at least one special character.')
  }

  if (!upperCaseChars.test(password.value)) {
    error.value.push('Password must contain at least one uppercase character.')
  }

  if (password.value !== confirmPassword.value) {
    error.value.push('Passwords do not match.')
  }

  if (error.value.length > 0) {
    return
  }

  const token = route.query.token
  console.log("Token" , token)
  if (!token) {
    return
  }
  try {
    const response = await api.post('/users/reset-password', {
      token: token,
      new_password: password.value,
    })
    if (response.status == 200) {
      submitted.value = true
      setTimeout(() => {
        router.push({name: "Login"})
      },5000);
    }
  } catch (err) {
    if (err instanceof Error) throw new Error(`Error while resetting the password : ${err}`)
  }
}
</script>

<template>
  <div class="grid min-h-screen place-items-center bg-background p-6">
    <div
      class="flex w-full max-w-4xl overflow-hidden rounded-2xl bg-sidebar-foreground shadow-lg ring-1 ring-border"
    >
      <div class="flex w-1/2 flex-col justify-center bg-sidebar p-10 text-sidebar-foreground">
        <p class="mb-3 text-sm font-medium uppercase tracking-[0.2em] text-sidebar-foreground/80">
          Secure access
        </p>
        <h1 class="text-3xl font-bold leading-tight">Create a new password</h1>
        <p class="mt-4 text-sm leading-6 text-sidebar-foreground/80">
          Choose a strong password and confirm it below to restore access to your account.
        </p>

        <section class="mt-8">
          <h2 class="font-semibold">Password requirements</h2>
          <dl class="mt-2 text-sm text-sidebar-foreground/80">
            <dd class="ms-0">Min length: 8 characters.</dd>
            <dd class="ms-0">At least one special character.</dd>
            <dd class="ms-0">At least one uppercase character.</dd>
          </dl>
        </section>
      </div>

      <form @submit.prevent="handleSubmit" class="w-1/2 bg-surface p-10">
        <div class="mb-6">
          <h2 class="text-2xl font-bold text-foreground">Reset password</h2>
          <p class="mt-2 text-sm text-foreground/70">Enter your new password twice.</p>
        </div>

        <div class="space-y-5">
          <div>
            <label for="password" class="mb-2 block text-sm font-medium text-foreground"
              >New password</label
            >
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              autocomplete="new-password"
              placeholder="Enter new password"
              class="w-full rounded-lg border border-border bg-white px-4 py-3 text-base text-foreground outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </div>

          <div>
            <label for="confirmPassword" class="mb-2 block text-sm font-medium text-foreground"
              >Confirm password</label
            >
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              name="confirmPassword"
              type="password"
              autocomplete="new-password"
              placeholder="Confirm new password"
              class="w-full rounded-lg border border-border bg-white px-4 py-3 text-base text-foreground outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </div>

          <DefaultButton type="submit" class="w-full"> Update password </DefaultButton>

          <ul
            v-if="error.length"
            class="space-y-2 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-foreground"
          >
            <li v-for="err in error" :key="err">{{ err }}</li>
          </ul>

          <div
            v-else-if="submitted"
            class="rounded-lg border border-success bg-success/20 px-4 py-3 text-sm text-foreground"
          >
            Your password has been updated successfully.
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped></style>
