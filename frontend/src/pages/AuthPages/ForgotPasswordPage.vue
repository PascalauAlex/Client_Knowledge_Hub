<script setup lang="ts">
import { ref } from 'vue'
import DefaultButton from '@/components/DefaultButton.vue'
import api from '@/services/api.ts'

const email = ref<string>('');
const submitted = ref<boolean>(false);
const error = ref<string>('');


const handleSubmit = async () => {
  if (!email.value.trim()) return

  try {
    const response = await api.post('/users/forgot-password', {"email" :email.value})

    if (response.status == 202 && response.data) {
      submitted.value = true;
    }
  } catch (err) {
    error.value = `Error while sending an email to: ${email.value}, please try again.`;
    if (err instanceof Error) throw new Error(error.value, err);
  }

  submitted.value = true
}
</script>

<template>
  <div class="grid min-h-screen place-items-center bg-background p-6">
    <div
      class="flex w-full max-w-4xl overflow-hidden rounded-2xl bg-sidebar-foreground shadow-lg ring-1 ring-border"
    >
      <div class="flex w-1/2 flex-col justify-center bg-sidebar p-10 text-sidebar-foreground">
        <p class="mb-3 text-sm font-medium uppercase tracking-[0.2em] text-sidebar-foreground/80">
          Account access
        </p>
        <h1 class="text-3xl font-bold leading-tight">Reset your password</h1>
        <p class="mt-4 text-sm leading-6 text-sidebar-foreground/80">
          Enter the email address associated with your account and we’ll send you the link to create
          a new password.
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="w-1/2 bg-surface p-10">
        <div class="mb-6">
          <h2 class="text-2xl font-bold text-foreground">Forgot password?</h2>
          <p class="mt-2 text-sm text-foreground/70">We’ll send a recovery email to your inbox.</p>
        </div>

        <div class="space-y-5">
          <div>
            <label for="email" class="mb-2 block text-sm font-medium text-foreground">Email</label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              autocomplete="email"
              placeholder="you@example.com"
              class="w-full rounded-lg border border-border bg-white px-4 py-3 text-base text-foreground outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </div>

          <DefaultButton type="submit" class="w-full"> Send reset link </DefaultButton>

          <div
            v-if="submitted"
            class="rounded-lg border border-success bg-success/20 px-4 py-3 text-sm text-foreground"
          >
            If an account exists for {{ email }}, a reset email has been sent.
          </div>

          <RouterLink
            :to="{ name: 'Login' }"
            class="mt-2 inline-block text-sm font-medium text-primary transition hover:underline"
          >
            Back to login
          </RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped></style>
