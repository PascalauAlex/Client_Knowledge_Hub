<script setup lang="ts">
import ActionBar from '@/components/ActionBar.vue'
import DefaultButton from '@/components/DefaultButton.vue'
import TableComponent, { type Column } from '@/components/TableComponent.vue'
import { onMounted, ref } from 'vue'
import api from '@/services/api.ts'
import router from '@/router'
import type { Client } from '@/types/client.ts'

const clients = ref<Client[]>([])



const columns: Column<Client>[] = [
  { key: 'id' , label:'No.' },
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'created_by', label: 'Created By' },
]

const getClients = async () => {
  try {
    const response = await api.get('/clients')
    if (response) {
      clients.value = response.data
    }
  } catch (err) {
    console.error(err)
  }
}

const goToClient = (client: Client) => {
  router.push({ name: 'SingleClient', params: { id: client.id } })
}

onMounted(async () => {
  await getClients()
})
</script>

<template>
  <div class="text-foreground mx-auto max-w-6xl space-y-8">
    <ActionBar>
      <template #default>
        <div class="relative flex items-center gap-4">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-accent text-accent-foreground shadow-sm"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M16 19v-1a4 4 0 00-4-4H6a4 4 0 00-4 4v1M9 10a3 3 0 100-6 3 3 0 000 6zM22 19v-1a4 4 0 00-3-3.9M16 4.1a3 3 0 010 5.8"
              />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-2xl font-bold tracking-tight">Clients</h1>
              <span
                class="rounded-full bg-surface/80 px-3 py-0.5 text-xs font-semibold text-foreground/70"
              >
                {{ clients.length }} total
              </span>
            </div>
            <p class="mt-1 text-sm text-foreground/70">
              Every client you manage, with their documents one click away.
            </p>
          </div>
        </div>

        <DefaultButton class="relative" @click="router.push({ name: 'AddClient' })">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 5v14M5 12h14" />
          </svg>
          Add Client
        </DefaultButton>
      </template>
    </ActionBar>

    <section class="overflow-hidden rounded-2xl border border-border/40 bg-surface shadow-sm">
      <div class="overflow-x-auto">
        <TableComponent
          :columns="columns"
          :rows="clients"
          row-key="id"
          empty-message="No clients yet. Add your first one to get started."
          @row-click="goToClient"
        >
          <template #cell-id="{ row }">
            <span
              class="inline-flex rounded-md bg-background px-2 py-0.5 font-mono text-xs text-foreground/60"
            >
              #{{ row.id }}
            </span>
          </template>

          <template #cell-name="{ row }">
            <RouterLink
              :to="{ name: 'SingleClient', params: { id: row.id } }"
              class="flex items-center gap-3"
            >
              <span
                class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent/60 text-sm font-bold text-accent-foreground transition group-hover:bg-accent"
              >
                {{ row.name.charAt(0).toUpperCase() }}
              </span>
              <span class="font-semibold">{{ row.name }}</span>
            </RouterLink>
          </template>

          <template #cell-email="{ row }">
            <span class="text-sm text-foreground/70">{{ row.email }}</span>
          </template>

          <template #cell-created_by="{ row }">
            <span
              class="inline-flex items-center gap-1.5 rounded-full bg-primary/20 px-3 py-1 text-xs font-semibold"
            >
              <span class="h-1.5 w-1.5 rounded-full bg-primary-hover"></span>
              {{ row.created_by.username }}
            </span>
          </template>
        </TableComponent>
      </div>
    </section>
  </div>
</template>

<style scoped></style>
