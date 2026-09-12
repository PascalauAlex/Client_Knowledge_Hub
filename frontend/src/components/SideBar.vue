<script setup lang="ts">
import type { Component } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  FileText,
  LayoutDashboard,
  Search,
  Settings,
  Users,
  CircleUser,
  Leaf,
  LogIn,
  UserPlus,
  LogOut,
} from 'lucide-vue-next'
import { deleteAccessToken } from '@/utils/LocalStorageUtils.ts'
import router from '@/router'

interface NavItem {
  label: string
  to: string
  icon: Component
}

const mainNav: NavItem[] = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Clients', to: '/clients', icon: Users },
  { label: 'Documents', to: '/documents', icon: FileText },
  { label: 'Search', to: '/search', icon: Search },
  { label: 'Account', to: '/account', icon: CircleUser },
]

const footerNav: NavItem[] = [{ label: 'Settings', to: '/settings', icon: Settings }]

const route = useRoute()

function isActive(to: string): boolean {
  return to === '/' ? route.path === '/' : route.path.startsWith(to)
}

const linkBase =
  'flex items-center gap-3 rounded-lg px-3 py-2.5 font-medium transition-colors ' +
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent'

function linkClass(to: string): string {
  return isActive(to)
    ? `${linkBase} bg-accent text-accent-foreground`
    : `${linkBase} hover:bg-white/10`
}

const logout = () => {
  deleteAccessToken()
  router.push('/')
}

function logOutClass(to : string): string{
  return isActive(to)
  ? `${linkBase} bg-accent text-accent-foreground`
    : `${linkBase} hover:bg-accent hover:text-foreground cursor-pointer`
}
</script>

<template>
  <aside class="flex h-screen w-64 shrink-0 flex-col bg-sidebar text-sidebar-foreground">
    <!-- Brand -->
    <div class="flex items-center gap-3 px-5 pt-8 pb-8">
      <div
        class="grid size-10 shrink-0 place-items-center rounded-xl bg-accent text-accent-foreground font-bold"
        aria-hidden="true"
      >
        <Leaf></Leaf>
      </div>
      <p class="text-lg font-bold leading-tight">Client<br />Knowledge Hub</p>
    </div>

    <!-- Main navbar -->
    <nav class="flex-1 overflow-y-auto px-3" aria-label="Main">
      <ul class="space-y-1">
        <li v-for="item in mainNav" :key="item.to">
          <RouterLink :to="item.to" :class="linkClass(item.to)">
            <component :is="item.icon" class="size-5 shrink-0" :stroke-width="1.75" />
            <span class="font-semibold">{{ item.label }}</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink class="font-semibold" :class="linkClass('/log-in')" :to="{ name: 'Login' }"
            ><component :is="LogIn" class="size-5 shrink-0" :stroke-width="1.75" />
            LogIn</RouterLink
          >
        </li>
        <li>
          <RouterLink class="font-semibold" :class="linkClass('/sign-up')" :to="{ name: 'Signup' }"
            ><component :is="UserPlus" class="size-5 shrink-0" :stroke-width="1.75" />
            SignUp</RouterLink
          >
        </li>
        <li>
          <button class="font-semibold w-full" :class="logOutClass('/log-out')" @click="logout">
            <component :is="LogOut" class="size-5 shrink-0" :stroke-width="1.75" />
            LogOut
          </button>
        </li>
      </ul>
    </nav>

    <!-- Setting -->
    <div class="border-t border-white/20 px-3 py-4">
      <ul class="space-y-1">
        <li v-for="item in footerNav" :key="item.to">
          <RouterLink :to="item.to" :class="linkClass(item.to)">
            <component :is="item.icon" class="size-5 shrink-0" :stroke-width="1.75" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </li>
      </ul>
    </div>
  </aside>
</template>
