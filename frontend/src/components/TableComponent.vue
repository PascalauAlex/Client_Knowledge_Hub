<script setup lang="ts" generic="T extends Record<string, any>">
import { useRouter } from 'vue-router'

export interface Column<R> {
  key: keyof R & string
  label: string
}

withDefaults(
  defineProps<{
    columns: Column<T>[]
    rows: T[]
    rowKey: keyof T & string
    emptyMessage?: string

  }>(),
  { emptyMessage: 'No data loaded...' },
)

const emit = defineEmits<{ rowClick: [row: T] }>()
</script>

<template>
  <table class="data-table">
    <thead>
      <tr>
        <th class="font-bold text-2xl" v-for="col in columns" :key="col.key">{{ col.label }}</th>
      </tr>
    </thead>

    <tbody>
      <tr v-if="rows.length === 0">
        <td :colspan="columns.length" class="data-table__empty">
          {{ emptyMessage }}
        </td>
      </tr>

      <tr
        v-for="row in rows"
        :key="String(row[rowKey])"
        class="hover:bg-accent transition cursor-pointer font-semibold"
        @click="emit('rowClick', row)"
      >
        <td v-for="col in columns" :key="col.key">
          <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
            {{ row[col.key] }}
          </slot>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.6rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  font-weight: 600;
  color: #374151;
  background: #f9fafb;
}

.data-table__empty {
  text-align: center;
  color: #6b7280;
  padding: 1.5rem;
}
</style>
