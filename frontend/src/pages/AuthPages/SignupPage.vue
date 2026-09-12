<script setup lang="ts">
import { ref } from 'vue'
import DefaultButton from '@/components/DefaultButton.vue'
import api from '@/services/api.ts'
import { useRouter } from 'vue-router'

const username = ref<string>('')
const email = ref<string>('')
const password = ref<string>('')
const isLoading = ref<boolean>(false)
const error = ref<string[]>([])

function isValidEmailSyntax(email: string) {
  if (typeof email !== 'string') return false
  if (email.length > 254) return false // RFC 5321 SMTP limit

  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/
  return pattern.test(email.trim())
}
const router = useRouter()
const SPECIAL_CHARS = /[!"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]/
const upperCaseChars = /[A-Z]/

const handleSubmit = async () => {
  error.value = []
  if (email.value && password.value && username.value) {
    email.value = email.value?.toLowerCase()
    const validEmail = isValidEmailSyntax(email.value)
    if (!validEmail) {
      error.value.push('Email is invalid. Try again with another email address.')
    }
    if (!SPECIAL_CHARS.test(password.value)) {
      error.value.push('Password must contain at least one special character.')
    }
    if (!upperCaseChars.test(password.value)) {
      error.value.push('Password must contain at least one uppercase character.')
    }
    if (password.value.length <= 8) {
      error.value.push('Password should contain 8 or more characters.')
    }
  }

  if (error.value.length > 0) {
    email.value = ''
    username.value = ''
    password.value = ''
    return
  }


  try {
    const response = await api.post('/users',
      {
        username: username.value,
        email : email.value,
        password: password.value

      })
    if (response.status == 201) {
      router.push({ name: 'Dashboard' })
    }
  } catch (err) {
    console.error(err)
    error.value.push(String(err))
  }
}
</script>

<template>
  <div class="grid min-h-full place-items-center">
    <div class="flex bg-sidebar-foreground p-10 rounded-2xl justify-center w-2/3">
      <div class="w-4xl">
        <h1 class="text-2xl font-semibold">Create your account</h1>
        <p>Sign up with your email and a password to start managing your clients!</p>
        <section>
          <h2 class="font-semibold">Requirements</h2>
          <dl class="mt-1 text-sm">
            <dt class="font-medium text-foreground">Username</dt>
            <dd class="ms-0 text-muted-foreground">Min length: 8 characters.</dd>
            <dd class="ms-0 text-muted-foreground">Max length: 50 characters.</dd>
          </dl>
          <dl class="mt-1 text-sm">
            <dt class="font-medium text-foreground">Password</dt>
            <dd class="ms-0 text-muted-foreground">Min length: 8 characters.</dd>
            <dd class="ms-0 text-muted-foreground">
              At least one of special characters [ {{ SPECIAL_CHARS }} ].
            </dd>
            <dd class="ms-0 text-muted-foreground">At least one uppercase character.</dd>
          </dl>
        </section>
      </div>
      <form @submit.prevent="handleSubmit" class="w-full max-w-sm">
        <div>
          <h1 class="text-foreground text-shadow-2xs text-2xl font-bold mb-4">Sign up</h1>
        </div>
        <div class="flex flex-col gap-4">
          <input
            v-model="username"
            placeholder="Username"
            name="username"
            type="text"
            autocomplete="username"
            class="w-full border border-border rounded-lg px-4 py-3 text-base"
          />
          <input
            v-model="email"
            placeholder="Email"
            name="email"
            type="email"
            autocomplete="email"
            class="w-full border border-border rounded-lg px-4 py-3 text-base"
          />
          <input
            v-model="password"
            placeholder="Password"
            name="password"
            type="password"
            autocomplete="new-password"
            minlength="8"
            class="w-full border border-border rounded-lg px-4 py-3 text-base"
          />
          <DefaultButton type="submit" :disabled="isLoading">
            {{ isLoading ? 'Loading...' : 'Sign up' }}
          </DefaultButton>
        </div>
        <RouterLink :to="{ name: 'Login' }" class="text-primary hover:underline cursor-pointer">
          Already have an account?
        </RouterLink>
        <ul>
          <li v-for="err in error" :key="err">{{ err }}</li>
        </ul>
      </form>
    </div>
  </div>
</template>

<style scoped></style>
