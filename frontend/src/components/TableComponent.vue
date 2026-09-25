<script setup lang="ts" generic="T extends Record<string, any>">


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
        <th
          class="bg-background text-xs font-semibold tracking-wide text-foreground/60 uppercase"
          v-for="col in columns"
          :key="col.key"
        >
          {{ col.label }}
        </th>
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
        class="group cursor-pointer transition hover:bg-accent/25"
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
  padding: 0.9rem 1.25rem;
  text-align: left;
  border-bottom: 1px solid color-mix(in srgb, var(--palette-cool-steel) 25%, transparent);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table__empty {
  text-align: center;
  color: color-mix(in srgb, var(--palette-ink) 60%, transparent);
  padding: 3rem 1.5rem;
}
</style>
