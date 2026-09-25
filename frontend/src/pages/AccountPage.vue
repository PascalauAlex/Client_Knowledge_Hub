<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import api from '@/services/api.ts'
import { getAccessToken } from '@/utils/LocalStorageUtils.ts'
import router from '@/router'
import type { User } from '@/types/user.ts'
import { formatDate } from '@/utils/formatDate'
import config from '@/config.ts'

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
  <div class="flex items-center justify-center bg-background p-6">
    <div
      class="grid w-2/3 grid-cols-1 gap-6 rounded-lg border border-border bg-accent p-4 md:grid-cols-2"
    >
      <div class="font-semibold">
        <img class="inline h-20 w-20 rounded-full" :src="avatarSrc" alt="" />
        <h1 class="ml-2 inline text-2xl font-bold">{{ user?.username || 'N/A' }}</h1>
        <p>
          Email: <span>{{ user?.email || 'N/A' }}</span>
        </p>
        <p>
          Created at: <span>{{ formatDate(user?.created_at) }}</span>
        </p>
      </div>

      <div class="border-t border-border/50 pt-6 md:border-t-0 md:border-l md:pt-0 md:pl-6">
        <h2 class="text-lg font-bold">Settings</h2>
        <div>
          <button class="block cursor-pointer hover:underline">Change password</button>
          <label for="profile_picture" class="hover:underline cursor-pointer"
            >Upload profile picture</label
          >
          <input
            @change="handleFileSelect"
            type="file"
            id="profile_picture"
            name="profile_picture"
            hidden="hidden"
          />

          <button
            class="block cursor-pointer hover:underline disabled:cursor-not-allowed disabled:opacity-50"
            v-if="profilePicture"
            :disabled="!profilePicture"
            @click="handleUpload"
          >
            Upload
          </button>
          <div v-if="errorMessageFile">
            <p>{{errorMessageFile}}</p>
            <button @click="profilePicture = null">Remove file </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
