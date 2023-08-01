import HomeView from '@/views/HomeView.vue'
import PrivacyAndCookieStatement from '@/views/PrivacyAndCookieStatement.vue'
import TermsOfService from '@/views/TermsOfService.vue'
import { createRouter, createWebHistory } from 'vue-router'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: HomeView
    },
    {
      path: '/privacy-and-cookie-statement',
      name: 'privacy_cookie_statement',
      component: PrivacyAndCookieStatement
    },
    {
      path: '/terms-of-service',
      name: 'terms-of-service',
      component: TermsOfService
    }
  ]
})

export default router
