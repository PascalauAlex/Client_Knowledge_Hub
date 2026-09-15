<script setup lang="ts">
import { nextTick, ref } from 'vue'
import type { Message, Source } from '../types/chat'
import api from '@/services/api.ts'

const props = defineProps<{ clientId: number }>()

const messages = ref<Message[]>([])
const question = ref('')
const loading = ref(false)
const logEl = ref<HTMLElement | null>(null)

async function send() {
  const query = question.value.trim()
  if (!query || loading.value) return

  messages.value.push({ role: 'user', content: query })
  question.value = ''
  loading.value = true

  try {
    const res = await api.post(`/clients/${props.clientId}/query`, null, {
      params: { query },
    })
    const data: { answer: string; sources: Source[] } = res.data
    messages.value.push({ role: 'assistant', content: data.answer, sources: data.sources })
  } catch {
    messages.value.push({ role: 'assistant', content: 'Could not get an answer. Try again.' })
  } finally {
    loading.value = false
    await nextTick()
    logEl.value?.scrollTo(0, logEl.value.scrollHeight)
  }
}
</script>

<template>
  <section class="flex h-full flex-col rounded-lg shadow-sm bg-surface">
    <div ref="logEl" class="flex flex-1 flex-col gap-3 overflow-y-auto p-4">
      <p v-if="!messages.length" class="text-foreground/60">
        Ask something about this client's documents.
      </p>

      <div
        v-for="(m, i) in messages"
        :key="i"
        :class="
          m.role === 'user'
            ? 'max-w-[80%] self-end rounded-lg bg-accent px-3 py-2 text-accent-foreground'
            : 'max-w-[80%] self-start border-l-2 border-primary pl-3'
        "
      >
        <p class="whitespace-pre-wrap">{{ m.content }}</p>

        <ul v-if="m.sources?.length" class="mt-2 flex flex-wrap gap-2 text-sm">
          <li v-for="s in m.sources" :key="s.id">
            <a
              :href="s.url ?? undefined"
              target="_blank"
              rel="noopener"
              class="rounded border border-border px-2 py-0.5 hover:bg-primary"
              >{{ s.title }}</a
            >
          </li>
        </ul>
      </div>

      <p v-if="loading" class="text-foreground/60">Searching the documents…</p>
    </div>

    <form class="flex gap-2 border-t border-border p-3" @submit.prevent="send">
      <input
        v-model="question"
        placeholder="Ask a question…"
        class="flex-1 rounded-md border border-gray-100 bg-surface px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
      />
      <button
        :disabled="loading || !question.trim()"
        class="rounded-md bg-primary px-4 py-2 font-medium text-primary-foreground hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50"
      >
        Send
      </button>
    </form>
  </section>
</template>


