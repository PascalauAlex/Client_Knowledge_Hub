import { createRouter, createWebHistory } from 'vue-router'
import DashboardPage from '@/pages/DashboardPage.vue'
import ClientsPage from '@/pages/ClientsPage.vue'
import AccountPage from '@/pages/AccountPage.vue'
import LoginPage from '@/pages/AuthPages/LoginPage.vue'
import SignupPage from '@/pages/AuthPages/SignupPage.vue'
import DocumentsPage from '@/pages/DocumentsPage.vue'
import SingleClientPage from '@/pages/SingleClientPage.vue'
import ForgotPasswordPage from '@/pages/AuthPages/ForgotPasswordPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: DashboardPage, name: 'Dashboard', meta: { title: 'Dashboard' } },
    {
      path: '/clients',
      component: ClientsPage,
      name: 'Clients',
      meta: { title: 'Client', requiresAuth: true },
    },
    {
      path: '/account',
      component: AccountPage,
      name: 'Account',
      meta: { title: 'Account', requiresAuth: true },
    },
    {
      path: '/documents',
      component: DocumentsPage,
      name: 'Documents',
      meta: { title: 'Documents', requiresAuth: true },
    },
    {
      path: '/log-in',
      component: LoginPage,
      name: 'Login',
      meta: { title: 'Login' },
    },
    { path: '/sign-up',
      component: SignupPage,
      name: 'Signup',
      meta: { title: 'Signup' } },
    {
      path: '/forgot-password',
      component:ForgotPasswordPage,
      name: 'ForgotPassword',
      meta: {title : 'ForgotPassword'},
    },
    {
      path : '/client/:id',
      component:SingleClientPage,
      name:'SingleClient',
      meta:{title: 'Client',
        requiresAuth: true}
    },

  ],
})

router.beforeEach((to, from) => {
  if (to.meta.requiresAuth){
    const token = localStorage.getItem("access_token");
    if(token){
      return true
    }
    else {
      return "/log-in";
    }
  }else{
    return true
  }
})




export default router
