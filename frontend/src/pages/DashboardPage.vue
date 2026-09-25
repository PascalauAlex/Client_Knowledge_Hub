<script setup lang="ts"></script>

<template>
  <div class="text-foreground mx-auto max-w-5xl space-y-12 p-6">
    <!-- Hero -->
    <section
      class="relative overflow-hidden rounded-2xl border border-accent bg-linear-to-br from-accent/40 via-surface to-primary/20 px-8 py-14 text-center shadow-sm"
    >
      <div class="absolute -top-16 -right-16 h-48 w-48 rounded-full bg-accent/40 blur-3xl"></div>
      <div class="absolute -bottom-20 -left-20 h-56 w-56 rounded-full bg-primary/30 blur-3xl"></div>

      <div class="relative space-y-5">
        <span
          class="inline-flex items-center gap-2 rounded-full bg-accent px-4 py-1 text-xs font-semibold tracking-wide text-accent-foreground uppercase"
        >
          <span class="h-2 w-2 rounded-full bg-foreground/70"></span>
          Client Knowledge Hub
        </span>
        <h1 class="text-4xl font-bold tracking-tight md:text-5xl">
          The memory of every client,
          <span class="text-primary-hover">one question away.</span>
        </h1>
        <p class="mx-auto max-w-2xl text-lg text-foreground/70">
          Upload a client's documents and ask anything about them. Answers come only from that
          client's own data, with sources.
        </p>
      </div>
    </section>

    <!-- How it works -->
    <section class="space-y-6">
      <div class="text-center">
        <h2 class="text-2xl font-semibold">How it works</h2>
        <div class="mx-auto mt-2 h-1 w-12 rounded-full bg-accent"></div>
      </div>

      <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div
          class="group rounded-2xl border border-border/40 bg-surface p-6 shadow-sm transition hover:-translate-y-1 hover:border-accent hover:shadow-md"
        >
          <div
            class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent/50 text-accent-foreground transition group-hover:bg-accent"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 16V4m0 0l-4 4m4-4l4 4M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" />
            </svg>
          </div>
          <p class="text-xs font-semibold text-primary-hover">STEP 1</p>
          <h3 class="mt-1 text-lg font-semibold">Upload</h3>
          <p class="mt-2 text-sm text-foreground/70">
            Add reports, contracts and invoices to a client. Files are stored securely in the cloud.
          </p>
        </div>

        <div
          class="group rounded-2xl border border-border/40 bg-surface p-6 shadow-sm transition hover:-translate-y-1 hover:border-accent hover:shadow-md"
        >
          <div
            class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent/50 text-accent-foreground transition group-hover:bg-accent"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.5 2a3.5 3.5 0 00-3.4 4.3A3.5 3.5 0 004 12a3.5 3.5 0 002.1 5.7A3.5 3.5 0 0012 20V4.5A2.5 2.5 0 009.5 2zM14.5 2a3.5 3.5 0 013.4 4.3A3.5 3.5 0 0120 12a3.5 3.5 0 01-2.1 5.7A3.5 3.5 0 0112 20" />
            </svg>
          </div>
          <p class="text-xs font-semibold text-primary-hover">STEP 2</p>
          <h3 class="mt-1 text-lg font-semibold">Understand</h3>
          <p class="mt-2 text-sm text-foreground/70">
            Documents are read, split and indexed by meaning. Invoices become structured data.
          </p>
        </div>

        <div
          class="group rounded-2xl border border-border/40 bg-surface p-6 shadow-sm transition hover:-translate-y-1 hover:border-accent hover:shadow-md"
        >
          <div
            class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent/50 text-accent-foreground transition group-hover:bg-accent"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h8M8 14h5m-9 6l2.5-3H18a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v14z" />
            </svg>
          </div>
          <p class="text-xs font-semibold text-primary-hover">STEP 3</p>
          <h3 class="mt-1 text-lg font-semibold">Ask</h3>
          <p class="mt-2 text-sm text-foreground/70">
            Ask in plain language and get answers grounded in the client's documents, with the page
            they came from.
          </p>
        </div>
      </div>
    </section>

    <!-- What's inside -->
    <section class="space-y-6">
      <div class="text-center">
        <h2 class="text-2xl font-semibold">What's inside</h2>
        <div class="mx-auto mt-2 h-1 w-12 rounded-full bg-accent"></div>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div class="flex gap-4 rounded-2xl border border-border/40 bg-surface p-5 shadow-sm transition hover:border-accent">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/50 text-accent-foreground">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h10M4 18h6" />
            </svg>
          </div>
          <div>
            <h3 class="font-semibold">Automatic summaries</h3>
            <p class="mt-1 text-sm text-foreground/70">Long documents turned into short, scannable insights.</p>
          </div>
        </div>

        <div class="flex gap-4 rounded-2xl border border-border/40 bg-surface p-5 shadow-sm transition hover:border-accent">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/50 text-accent-foreground">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6M9 11h6M9 15h3M6 3h12v18l-3-2-3 2-3-2-3 2V3z" />
            </svg>
          </div>
          <div>
            <h3 class="font-semibold">Invoice extraction</h3>
            <p class="mt-1 text-sm text-foreground/70">Vendor, dates, items and total pulled out automatically.</p>
          </div>
        </div>

        <div class="flex gap-4 rounded-2xl border border-border/40 bg-surface p-5 shadow-sm transition hover:border-accent">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/50 text-accent-foreground">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 3h7l5 5v13H7V3zM14 3v5h5" />
            </svg>
          </div>
          <div>
            <h3 class="font-semibold">Many file formats</h3>
            <p class="mt-1 text-sm text-foreground/70">PDF, Word, Excel and CSV, checked before every upload.</p>
          </div>
        </div>

        <div class="flex gap-4 rounded-2xl border border-border/40 bg-surface p-5 shadow-sm transition hover:border-accent">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/50 text-accent-foreground">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 7a3 3 0 11-6 0 3 3 0 016 0zM5 21a7 7 0 0114 0" />
            </svg>
          </div>
          <div>
            <h3 class="font-semibold">Your own workspace</h3>
            <p class="mt-1 text-sm text-foreground/70">Secure sign-in and password recovery by email.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Principles -->
    <section class="rounded-2xl bg-sidebar p-8 text-sidebar-foreground shadow-sm">
      <div class="grid grid-cols-1 gap-8 text-center sm:grid-cols-2 lg:grid-cols-4">
        <div class="space-y-2">
          <div class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-accent text-accent-foreground">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z" />
            </svg>
          </div>
          <h4 class="font-semibold">Isolated per client</h4>
          <p class="text-sm text-sidebar-foreground/80">You only ever see your clients' data.</p>
        </div>
        <div class="space-y-2">
          <div class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-accent text-accent-foreground">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h4 class="font-semibold">Cited answers</h4>
          <p class="text-sm text-sidebar-foreground/80">Every answer points back to its source.</p>
        </div>
        <div class="space-y-2">
          <div class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-accent text-accent-foreground">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 11V8a6 6 0 0112 0v3M5 11h14v10H5V11z" />
            </svg>
          </div>
          <h4 class="font-semibold">Private file access</h4>
          <p class="text-sm text-sidebar-foreground/80">Files open through secure, time-limited links.</p>
        </div>
        <div class="space-y-2">
          <div class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-accent text-accent-foreground">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 12a8 8 0 0114-5.3M20 12a8 8 0 01-14 5.3M18 3v4h-4M6 21v-4h4" />
            </svg>
          </div>
          <h4 class="font-semibold">Reliable uploads</h4>
          <p class="text-sm text-sidebar-foreground/80">If processing fails, nothing is left half-saved.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped></style>
