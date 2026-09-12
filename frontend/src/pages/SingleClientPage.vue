<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FileText, SquarePen, Trash, Upload } from 'lucide-vue-next'

import api from '@/services/api.ts'
import DefaultButton from '@/components/DefaultButton.vue'
import BaseModal from '@/components/BaseModal.vue'

import type { Client } from '@/types/client.ts'
import type { Documents } from '@/types/documents.ts'
import config from '../config'

const route = useRoute()
const router = useRouter()

const client = ref<Client>()
const documents = ref<Documents[]>([])
const file = ref<File[]>([])

/* ---------- fetch ---------- */

const getClientDetails = async (clientId: number) => {
  try {
    const response = await api.get(`/clients/${clientId}`)
    client.value = response.data
  } catch (err) {
    console.error(err)
  }
}

const getClientDocuments = async (clientId: number) => {
  try {
    const response = await api.get(`/clients/documents/${clientId}`)
    documents.value = response.data
  } catch (err) {
    console.error(err)
  }
}

const load = async (clientId: number) => {
  await Promise.all([getClientDetails(clientId), getClientDocuments(clientId)])
}

onMounted(() => load(Number(route.params.id)))

watch(
  () => route.params.id,
  (id) => id && load(Number(id)),
)

/* ---------- edit ---------- */

const editModal = ref(false)



/* ---------- delete ---------- */

const deleteModal = ref(false)
const confirmName = ref('')
const deleting = ref(false)

const canDelete = computed(() => confirmName.value.trim() === client.value?.name && !deleting.value)

watch(deleteModal, (open) => {
  if (!open) confirmName.value = ''
})

const handleClientDelete = async () => {
  if (!canDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/clients/${route.params.id}`)
    router.push({ name: 'Clients' })
  } catch (err) {
    console.error(err)
  } finally {
    deleting.value = false
  }
}

/* ---------- Upload ----------- */
const errorMessageFile = ref<string | null>()

const handleUpload = async (e: Event) => {
  const input = e.target as HTMLInputElement
  const selectedFile = Array.from(input?.files || [])

  const validFiles = selectedFile.filter((file) => {
    const sizeInMB = file.size / (1024 * 1024)
    if (sizeInMB > config.maxFileSizeMB) {
      errorMessageFile.value = `File ${file.name} exceeds the ${config.maxFileSizeMB} MB max file size.`
      return false
    } else {
      return true
    }
  })

  file.value = file.value.concat(validFiles)

  if (!file.value[0]) {
    return
  }

  try {
    const client_id = String(route.params.id)
    const fileFormData = new FormData()
    const params = new URLSearchParams()
    params.append('name', file.value[0].name)
    params.append('client_id', client_id)
    params.append('doc_type', 'report')

    fileFormData.append('file', file.value[0])
    const response = await api.post('/documents/upload/', fileFormData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: params,
    })

    if (response.status == 201) {
      console.log('SUCCESS FILE UPLOADED.')
    }
  } catch (err) {
    console.error(err)
  }
}

/* ---------- helpers ---------- */

const formatDate = (value: string) =>
  new Date(value).toLocaleDateString('ro-RO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
</script>

<template>
  <div class="p-6">
    <div v-if="client" class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Card client -->
      <section class="h-fit rounded-xl bg-surface p-6 shadow-sm lg:col-span-1">
        <h2 class="text-lg font-semibold">{{ client.name }}</h2>
        <p class="mt-1 text-sm text-foreground/60">ID #{{ client.id }}</p>

        <dl class="mt-6 space-y-4">
          <div>
            <dt class="text-xs font-medium uppercase tracking-wide text-foreground/60">Email</dt>
            <dd class="mt-1 text-sm">{{ client.email }}</dd>
          </div>
          <div>
            <dt class="text-xs font-medium uppercase tracking-wide text-foreground/60">
              Created by
            </dt>
            <dd class="mt-1 text-sm">{{ client.created_by?.username ?? '—' }}</dd>
          </div>
        </dl>

        <div class="mt-8">
          <h3 class="text-xs font-medium uppercase tracking-wide text-foreground/60">Actions</h3>
          <div class="mt-3 flex gap-2">
            <DefaultButton class="flex-1" @click="editModal = true">
              <SquarePen class="h-4 w-4" /> Edit
            </DefaultButton>
            <DefaultButton style-type="danger" class="flex-1" @click="deleteModal = true">
              <Trash class="h-4 w-4" /> Delete
            </DefaultButton>
          </div>
        </div>
      </section>

      <!-- Documents card -->
      <section class="rounded-xl bg-surface p-6 shadow-sm lg:col-span-2">
        <header class="mb-4 flex items-center justify-between gap-4">
          <div class="flex items-center gap-2">
            <h2 class="text-lg font-semibold">Documents</h2>
            <span
              class="rounded-full bg-background px-2 py-0.5 text-xs font-medium text-foreground/60"
            >
              {{ documents.length }}
            </span>
          </div>

          <div
            class="font-semibold border border-white hover:border hover:border-border p-1 rounded-lg"
          >
            <component class="inline mr-1" :is="Upload"></component>
            <label for="file-input" class="cursor-pointer">Upload</label>
            <input
              @change="handleUpload"
              id="file-input"
              type="file"
              accept="application/pdf, .doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document, "
              hidden="hidden"
            />
          </div>
        </header>
          <ul v-if="documents.length" class="space-y-1 overflow-y-auto max-h-64">
            <li
              v-for="doc in documents"
              :key="doc.id"
              class="flex items-center gap-3 rounded-lg px-2 py-3 transition hover:bg-background"
            >
              <FileText class="h-5 w-5 shrink-0 text-foreground/50" />

              <div class="min-w-0 flex-1">
                <a
                  :href="doc.file"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="block truncate text-sm font-semibold hover:underline"
                >
                  {{ doc.name }}
                </a>
                <p class="mt-0.5 text-xs text-foreground/60">{{ formatDate(doc.created_at) }}</p>
              </div>
            </li>
          </ul>
        <p v-else class="py-8 text-center text-sm text-foreground/60">No documents...</p>
      </section>
    </div>

    <p v-else class="text-sm text-foreground/60">Loading…</p>

    <!-- Edit -->

    <!-- Delete -->
    <BaseModal
      v-model="deleteModal"
      title="Delete client"
      description="Associated documents will be erased."
    >
      <p class="text-sm text-foreground/70">
        This action cannot be reversed. Write
        <strong class="text-foreground">{{ client?.name }}</strong>
        to confirm.
      </p>

      <input
        v-model="confirmName"
        type="text"
        :placeholder="client?.name"
        autocomplete="off"
        class="mt-3 w-full rounded-lg border  bg-surface px-3 py-2 text-sm transition placeholder:text-foreground/40 focus:border-destructive focus:outline-none focus:ring-2 focus:ring-destructive/40"
        @keyup.enter="handleClientDelete"
      />

      <template #footer>
        <button
          class="border border-border hover:border-white hover:bg-border p-2 rounded-lg hover:text-white"
          :disabled="deleting"
          @click="deleteModal = false"
        >
          CANCEL
        </button>

        <DefaultButton style-type="danger" :disabled="!canDelete" @click="handleClientDelete">
          {{ deleting ? 'Deleting...' : 'Delete' }}
        </DefaultButton>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped></style>
