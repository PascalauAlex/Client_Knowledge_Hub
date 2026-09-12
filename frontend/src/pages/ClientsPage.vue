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
  <div>
    <ActionBar>
      <template #default>
        <DefaultButton>
          Add Client
        </DefaultButton>
      </template>
    </ActionBar>
    <div class="mt-10">
      <TableComponent :columns="columns" :rows="clients" row-key="id" @row-click="goToClient">
        <template #cell-name="{ row }">
          <RouterLink :to="{ name: 'SingleClient', params: { id: row.id } }" class="hover:text-white">
            {{ row.name }}
          </RouterLink>
        </template>
        <template #cell-created_by="{ row }">
          <div @click="router.push(`/client/${row.id}`)">
            {{ row.created_by.username }}
          </div>
        </template>
      </TableComponent>
    </div>
  </div>
</template>

<style scoped></style>
