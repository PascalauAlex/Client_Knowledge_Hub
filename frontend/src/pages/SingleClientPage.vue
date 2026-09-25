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
import ChatComponent from '@/components/ChatComponent.vue'

const route = useRoute()
const router = useRouter()

const client = ref<Client>()
const documents = ref<Documents[]>([])
const file = ref<File[]>([])
const client_id = ref(Number(route.params.id))

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

const deleteModal = ref<boolean>(false)
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

/* ---------- Delete document ------- */

const documentModalActive = ref<boolean>(false)
const documentToDelete = ref<Documents | null>(null)
const deletingDocument = ref<boolean>(false)
const documentDeleteConfirmation = ref<string>('')

const activateDocumentDeleteModal = (document: Documents) => {
  documentToDelete.value = document
  documentModalActive.value = true
}

const canDeleteDocument = computed(() => {
  const doc = documentToDelete.value
  if (!doc) return false
  return (
    documentDeleteConfirmation.value.trim() === doc.name + doc.extension_type &&
    !deletingDocument.value
  )
})

watch(documentModalActive, (open) => {
  if (!open) {
    documentDeleteConfirmation.value = ''
    documentToDelete.value = null
  }
})

const handleDocumentDelete = async () => {
  const doc = documentToDelete.value
  if (!doc || !canDeleteDocument.value) return

  deletingDocument.value = true
  try {
    await api.delete('/documents/delete', {
      params: {
        document_id: doc.id,
        client_id: client.value?.id,
      },
    })
    documents.value = documents.value.filter((d) => d.id !== doc.id)
    documentModalActive.value = false
  } catch (err) {
    console.error(err)
  } finally {
    deletingDocument.value = false
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
  <div class="text-foreground mx-auto max-w-6xl space-y-8">
    <div v-if="client" class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Card client -->
      <section
        class="h-fit overflow-hidden rounded-2xl border border-accent bg-surface shadow-sm lg:col-span-1"
      >
        <div
          class="relative h-20 overflow-hidden bg-linear-to-br from-accent/60 via-accent/30 to-primary/40"
        >
          <div
            class="absolute -top-10 -right-10 h-32 w-32 rounded-full bg-accent/60 blur-3xl"
          ></div>
        </div>

        <div class="px-6 pb-6">
          <div
            class="-mt-8 flex h-16 w-16 items-center justify-center rounded-full bg-accent text-2xl font-bold text-accent-foreground shadow-md ring-4 ring-surface"
          >
            {{ client.name.charAt(0).toUpperCase() }}
          </div>
          <h2 class="mt-3 text-xl font-bold tracking-tight">{{ client.name }}</h2>
          <span
            class="mt-1 inline-flex rounded-md bg-background px-2 py-0.5 font-mono text-xs text-foreground/60"
          >
            #{{ client.id }}
          </span>

          <dl class="mt-6 space-y-4">
            <div>
              <dt class="text-xs font-medium uppercase tracking-wide text-foreground/60">Email</dt>
              <dd class="mt-1 text-sm">{{ client.email }}</dd>
            </div>
            <div>
              <dt class="text-xs font-medium uppercase tracking-wide text-foreground/60">
                Created by
              </dt>
              <dd class="mt-1">
                <span
                  class="inline-flex items-center gap-1.5 rounded-full bg-primary/20 px-3 py-1 text-xs font-semibold"
                >
                  <span class="h-1.5 w-1.5 rounded-full bg-primary-hover"></span>
                  {{ client.created_by?.username ?? '—' }}
                </span>
              </dd>
            </div>
          </dl>

          <div class="mt-8 border-t border-border/30 pt-6">
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
        </div>
      </section>

      <!-- Documents card -->
      <section class="rounded-2xl border border-border/40 bg-surface p-6 shadow-sm lg:col-span-2">
        <header class="mb-5 flex items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-lg font-semibold">Documents</h2>
              <span
                class="rounded-full bg-accent/40 px-2 py-0.5 text-xs font-semibold text-accent-foreground"
              >
                {{ documents.length }}
              </span>
            </div>
            <div class="mt-2 h-1 w-10 rounded-full bg-accent"></div>
          </div>

          <div>
            <label
              for="file-input"
              class="inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-accent bg-accent px-3.5 py-2 text-sm font-semibold text-accent-foreground shadow-sm transition hover:bg-accent-hover"
            >
              <component class="h-4 w-4" :is="Upload"></component>
              Upload
            </label>
            <input
              @change="handleUpload"
              id="file-input"
              type="file"
              accept="application/pdf, .doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document, "
              hidden="hidden"
            />
          </div>
        </header>
        <ul v-if="documents.length" class="max-h-64 space-y-2 overflow-y-auto pr-1">
          <li
            v-for="doc in documents"
            :key="doc.id"
            class="group flex items-center gap-3 rounded-xl border border-border/30 px-3 py-3 transition hover:border-accent hover:bg-accent/20"
          >
            <span
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/50 text-accent-foreground transition group-hover:bg-accent"
            >
              <FileText class="h-5 w-5" />
            </span>

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
            <button
              @click="activateDocumentDeleteModal(doc)"
              class="cursor-pointer rounded-lg p-2 text-foreground/40 transition hover:bg-destructive/10 hover:text-destructive"
              title="Delete document"
            >
              <Trash class="h-4 w-4" />
            </button>
          </li>
        </ul>
        <div
          v-else
          class="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border/50 py-10 text-center"
        >
          <span
            class="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/40 text-accent-foreground"
          >
            <FileText class="h-6 w-6" />
          </span>
          <p class="text-sm text-foreground/60">No documents yet.</p>
        </div>
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
        class="mt-3 w-full rounded-lg border bg-surface px-3 py-2 text-sm transition placeholder:text-foreground/40 focus:border-destructive focus:outline-none focus:ring-2 focus:ring-destructive/40"
        @keyup.enter="handleClientDelete"
      />

      <template #footer>
        <button
          class="cursor-pointer rounded-lg border border-border/50 px-3.5 py-2 text-sm font-semibold transition hover:bg-background disabled:opacity-50"
          :disabled="deleting"
          @click="deleteModal = false"
        >
          Cancel
        </button>

        <DefaultButton style-type="danger" :disabled="!canDelete" @click="handleClientDelete">
          {{ deleting ? 'Deleting...' : 'Delete' }}
        </DefaultButton>
      </template>
    </BaseModal>

    <!-- Delete Document Modal -->
    <BaseModal
      v-if="documentToDelete"
      v-model="documentModalActive"
      title="Delete document"
      description="Deleted documents cannot be restored after this procedure."
      :entity="documentToDelete"
    >
      <p class="text-sm text-foreground/70">
        Are you sure that you want to delete
        <strong class="text-foreground"
          >{{ documentToDelete.name }}{{ documentToDelete.extension_type }}</strong
        >? To confirm deletion please write
        <span class="rounded bg-background px-1 font-mono text-xs"
          >{{ documentToDelete.name }}{{ documentToDelete.extension_type }}</span
        >.
      </p>
      <input
        v-model="documentDeleteConfirmation"
        class="mt-3 w-full rounded-lg border bg-surface px-3 py-2 text-sm transition placeholder:text-foreground/40 focus:border-destructive focus:outline-none focus:ring-2 focus:ring-destructive/40"
        type="text"
        autocomplete="off"
        :placeholder="'Write: ' + documentToDelete.name + documentToDelete.extension_type"
        @keyup.enter="handleDocumentDelete"
      />

      <template #footer>
        <button
          class="cursor-pointer rounded-lg border border-border/50 px-3.5 py-2 text-sm font-semibold transition hover:bg-background disabled:opacity-50"
          :disabled="deletingDocument"
          @click="documentModalActive = false"
        >
          Cancel
        </button>
        <DefaultButton
          style-type="danger"
          :disabled="!canDeleteDocument"
          @click="handleDocumentDelete"
        >
          {{ deletingDocument ? 'Deleting...' : 'Delete' }}
        </DefaultButton>
      </template>
    </BaseModal>

    <div class="overflow-hidden rounded-2xl border border-border/40 shadow-sm">
      <ChatComponent :client-id="client_id"></ChatComponent>
    </div>
  </div>
</template>

<style scoped></style>
