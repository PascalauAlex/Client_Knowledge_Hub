<script setup lang="ts">
interface Props {
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  styleType?: 'primary' | 'danger'
}

const { type = 'button', disabled = false, styleType = 'primary' } = defineProps<Props>()

const base = `inline-flex items-center justify-center gap-1.5 rounded-lg border px-3.5 py-2
  text-sm font-semibold shadow-sm cursor-pointer select-none
  transition-colors duration-150 active:translate-y-px
  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
  disabled:pointer-events-none disabled:opacity-50`

const variants: Record<NonNullable<Props['styleType']>, string> = {
  primary: `bg-accent text-accent-foreground border-accent
    hover:bg-accent/90 hover:border-accent/90 focus-visible:ring-accent`,
  danger: `bg-destructive text-destructive-foreground border-destructive
    hover:bg-destructive/90 hover:border-destructive/90 focus-visible:ring-destructive`,
}
</script>

<template>
  <button :class="[base, variants[styleType]]" :type="type" :disabled="disabled">
    <slot />
  </button>
</template>
