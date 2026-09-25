<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import api from '@/services/api.ts'
import { getAccessToken } from '@/utils/LocalStorageUtils.ts'
import router from '@/router'
import type { User } from '@/types/user.ts'
import { formatDate } from '@/utils/formatDate'
import config from '@/config.ts'
import DefaultButton from '@/components/DefaultButton.vue'

const changePassword = ref<boolean>(false)

const fallBackAvatar = '/user-avatar.png'
const avatarSrc = ref<string>()
interface AccountDetails extends User {
  email: string
  created_at: string
  image_path: string | null
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

const profilePicture = ref<File | null>(null)
const errorMessageFile = ref<string>()

const handleUpload = async () => {
  if (!user.value?.id || !profilePicture.value) {
    return
  }
  const formData = new FormData()
  formData.append('file', profilePicture.value)
  try {
    const response = await api.post(`/users/upload_profile_picture`, formData, {
      params: { user_id: user.value.id },
    })
    user.value = response.data
    profilePicture.value = null
  } catch (err) {
    console.error(err)
  }
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  errorMessageFile.value = undefined
  profilePicture.value = null
  if (!file) {
    return
  }

  const sizeInMB = file.size / (1024 * 1024)
  if (sizeInMB > config.maxFileSizeMB) {
    errorMessageFile.value = `File ${file.name} exceeds the ${config.maxFileSizeMB} MB max file size.`
    return
  }
  profilePicture.value = file
}

/* Password change */

const current_password = ref<string>('')
const new_password = ref<string>('')
const redirectAnnounce = ref<string>()
const handleChangePassword = async () => {
  const formData = new FormData()
  formData.append('current_password', current_password.value)
  formData.append('new_password', new_password.value)

  try {
    const response = await api.post('/users/me/password', formData, {
      headers: { 'Content-Type': 'application/json' },
      validateStatus: (status) => {
        return status < 500
      },
    })

    switch (response.status) {
      case 200:
        redirectAnnounce.value =
          'Password change successful.\nYou will be redirected to LogIn in 5 seconds.'
        setTimeout(() => {
          router.push({ name: 'Login' })
        }, 5000)
        break
      case 400:
        redirectAnnounce.value = 'Password is incorrect, please try again.'
        break
      case 422:
        redirectAnnounce.value = 'Invalid password.'
        break
      default:
        redirectAnnounce.value = "Error while changing password, please try again."
        break;
    }
  } catch (err) {
    console.error(err)
  }
}
/* */

watch(
  () => user.value?.image_file,
  (url) => {
    avatarSrc.value = url ?? fallBackAvatar
  },
  { immediate: true },
)

onMounted(async () => {
  await getMe()
})
</script>

<template>
  <div class="text-foreground mx-auto max-w-4xl space-y-8">
    <!-- Profile header -->
    <section class="overflow-hidden rounded-2xl border border-accent bg-surface shadow-sm">
      <div
        class="relative h-32 overflow-hidden bg-linear-to-br from-accent/60 via-accent/30 to-primary/40"
      >
        <div class="absolute -top-12 -right-12 h-40 w-40 rounded-full bg-accent/60 blur-3xl"></div>
        <div
          class="absolute -bottom-16 left-1/3 h-40 w-40 rounded-full bg-primary/40 blur-3xl"
        ></div>
      </div>

      <div class="flex flex-col gap-4 px-6 pb-6 sm:flex-row sm:items-end">
        <div class="relative -mt-12 w-fit">
          <img
            class="h-24 w-24 rounded-full bg-background object-cover shadow-md ring-4 ring-surface"
            :src="avatarSrc"
            alt=""
          />
          <label
            for="profile_picture"
            class="absolute right-0 bottom-0 flex h-8 w-8 cursor-pointer items-center justify-center rounded-full bg-accent text-accent-foreground shadow-sm ring-2 ring-surface transition hover:bg-accent-hover"
            title="Change profile picture"
          >
            <svg
              class="h-4 w-4"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M4 8h3l2-3h6l2 3h3v11H4V8zM12 16a3 3 0 100-6 3 3 0 000 6z"
              />
            </svg>
          </label>
        </div>

        <div class="flex-1">
          <h1 class="text-2xl font-bold tracking-tight">{{ user?.username || 'N/A' }}</h1>
          <p class="text-sm text-foreground/70">{{ user?.email || 'N/A' }}</p>
        </div>

        <span
          class="inline-flex w-fit items-center gap-2 rounded-full bg-accent/40 px-3 py-1 text-xs font-semibold"
        >
          <span class="h-2 w-2 rounded-full bg-accent-hover"></span>
          Member since {{ formatDate(user?.created_at) }}
        </span>
      </div>
    </section>

    <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
      <!-- Account details -->
      <section class="rounded-2xl border border-border/40 bg-surface p-6 shadow-sm">
        <h2 class="text-lg font-semibold">Account details</h2>
        <div class="mt-2 h-1 w-10 rounded-full bg-accent"></div>

        <dl class="mt-6 space-y-5">
          <div>
            <dt class="text-xs font-medium tracking-wide text-foreground/60 uppercase">Username</dt>
            <dd class="mt-1 text-sm font-semibold">{{ user?.username || 'N/A' }}</dd>
          </div>
          <div>
            <dt class="text-xs font-medium tracking-wide text-foreground/60 uppercase">Email</dt>
            <dd class="mt-1 text-sm font-semibold">{{ user?.email || 'N/A' }}</dd>
          </div>
          <div>
            <dt class="text-xs font-medium tracking-wide text-foreground/60 uppercase">
              Created at
            </dt>
            <dd class="mt-1 text-sm font-semibold">{{ formatDate(user?.created_at) }}</dd>
          </div>
        </dl>
      </section>

      <!-- Settings -->
      <section class="rounded-2xl border border-border/40 bg-surface p-6 shadow-sm">
        <h2 class="text-lg font-semibold">Settings</h2>
        <div class="mt-2 h-1 w-10 rounded-full bg-accent"></div>

        <div class="mt-6 space-y-3">
          <button
            @click="changePassword = !changePassword"
            class="group flex w-full cursor-pointer items-center gap-4 rounded-xl border border-border/30 p-4 text-left transition hover:border-accent hover:bg-accent/20"
          >
            <span
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/50 text-accent-foreground transition group-hover:bg-accent"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M6 11V8a6 6 0 0112 0v3M5 11h14v10H5V11z"
                />
              </svg>
            </span>
            <span class="flex-1">
              <span class="block text-sm font-semibold">Change password</span>
              <span class="block text-xs text-foreground/60">Keep your account secure</span>
            </span>
            <span class="text-foreground/40 transition group-hover:translate-x-1">→</span>
          </button>

          <label
            for="profile_picture"
            class="group flex w-full cursor-pointer items-center gap-4 rounded-xl border border-border/30 p-4 transition hover:border-accent hover:bg-accent/20"
          >
            <span
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/50 text-accent-foreground transition group-hover:bg-accent"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M4 16l4-4 4 4 3-3 5 5M4 4h16v16H4V4zM15 9a1 1 0 100-2 1 1 0 000 2z"
                />
              </svg>
            </span>
            <span class="flex-1">
              <span class="block text-sm font-semibold">Upload profile picture</span>
              <span class="block text-xs text-foreground/60">
                Max {{ config.maxFileSizeMB }} MB
              </span>
            </span>
            <span class="text-foreground/40 transition group-hover:translate-x-1">→</span>
          </label>
          <input
            @change="handleFileSelect"
            type="file"
            id="profile_picture"
            name="profile_picture"
            hidden="hidden"
          />

          <div
            v-if="profilePicture"
            class="flex items-center gap-3 rounded-xl border border-accent bg-accent/20 p-3"
          >
            <span class="flex-1 truncate text-sm font-medium">{{ profilePicture.name }}</span>
            <button
              class="cursor-pointer rounded-lg px-3 py-1.5 text-xs font-semibold text-foreground/70 transition hover:bg-surface"
              @click="profilePicture = null"
            >
              Cancel
            </button>
            <button
              class="cursor-pointer rounded-lg bg-accent px-3 py-1.5 text-xs font-semibold text-accent-foreground shadow-sm transition hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="!profilePicture"
              @click="handleUpload"
            >
              Upload
            </button>
          </div>

          <div
            v-if="errorMessageFile"
            class="flex items-center gap-3 rounded-xl border border-destructive/40 bg-destructive/10 p-3"
          >
            <p class="flex-1 text-sm text-destructive">{{ errorMessageFile }}</p>
            <button
              class="cursor-pointer rounded-lg px-3 py-1.5 text-xs font-semibold text-destructive transition hover:bg-destructive/10"
              @click="profilePicture = null"
            >
              Remove file
            </button>
          </div>
        </div>
      </section>
      <section
        class="rounded-2xl border border-border/40 bg-surface p-6 shadow-sm"
        v-if="changePassword"
      >
        <div>
          <form @submit.prevent="handleChangePassword">
            <label for="current_password">Current password</label>
            <input
              v-model="current_password"
              name="current_password"
              id="current_password"
              type="password"
              placeholder="Your current password ..."
              class="rounded-lg border border-border p-2 block"
            />
            <label for="new_password">New password</label>
            <input
              v-model="new_password"
              id="new_password"
              name="new_password"
              type="password"
              placeholder="Your new password ..."
              class="rounded-lg border border-border p-2 block focus:border-border"
            />
            <DefaultButton class="mt-2" type="submit">Change password</DefaultButton>
            <p v-if="redirectAnnounce" class="font-semibold mt-2 bg-accent rounded-lg p-2">
              {{ redirectAnnounce }}
            </p>
          </form>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped></style>
