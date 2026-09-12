<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { X } from 'lucide-vue-next'

defineProps<{ title: string; description?: string }>()

const open = defineModel<boolean>({ required: true })
const dialog = ref<HTMLDialogElement | null>(null)

const sync = (value: boolean) => {
  const el = dialog.value
  if (!el) return

  if (value && !el.open) el.showModal()
  if (!value && el.open) el.close()

  document.documentElement.classList.toggle('overflow-hidden', value)
}

// La montare acoperim cazul în care modala pornește deja deschisă;
// watcher-ul singur nu s-ar declanșa, fiindcă valoarea nu se schimbă.
onMounted(() => sync(open.value))
watch(open, sync)

onBeforeUnmount(() => document.documentElement.classList.remove('overflow-hidden'))

// Click pe backdrop: target-ul este chiar <dialog>, nu panoul dinăuntru.
const onDialogClick = (event: MouseEvent) => {
  if (event.target === dialog.value) open.value = false
}
</script>

<template>
  <dialog
    ref="dialog"
    class="m-auto w-[calc(100%-2rem)] max-w-lg border-0 bg-transparent p-0 backdrop:bg-foreground/40 backdrop:backdrop-blur-[2px]"
    @close="open = false"
    @click="onDialogClick"
  >
    <div class="rounded-xl bg-surface text-foreground shadow-xl">
      <header class="flex items-start justify-between gap-4 px-5 pb-4 pt-5">
        <div class="min-w-0">
          <h2 class="text-base font-semibold">{{ title }}</h2>
          <p v-if="description" class="mt-1 text-sm text-foreground/60">{{ description }}</p>
        </div>

        <button
          type="button"
          aria-label="Închide"
          class="-mr-1 shrink-0 cursor-pointer rounded-lg p-1.5 text-foreground/60 transition hover:bg-background hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          @click="open = false"
        >
          <X class="h-4 w-4" />
        </button>
      </header>

      <div class="px-5 pb-5">
        <slot />
      </div>

      <footer
        v-if="$slots.footer"
        class="flex justify-end gap-2 rounded-b-xl bg-background/60 px-5 py-4"
      >
        <slot name="footer" />
      </footer>
    </div>
  </dialog>
</template>

<style scoped>
dialog[open] {
  animation: modal-in 160ms ease-out;
}

dialog[open]::backdrop {
  animation: backdrop-in 160ms ease-out;
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
  }
}

@keyframes backdrop-in {
  from {
    opacity: 0;
  }
}
</style>
