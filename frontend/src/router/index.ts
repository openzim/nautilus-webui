import HomeView from '@/views/HomeView.vue'
import ProjectView from '@/views/ProjectView.vue'
import PrivacyAndCookieStatement from '@/views/PrivacyAndCookieStatement.vue'
import TermsOfService from '@/views/TermsOfService.vue'
import { createRouter, createWebHistory } from 'vue-router'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomeView
    },
    {
      path: '/project',
      name: 'Project',
      component: ProjectView
    },
    {
      path: '/privacy-and-cookie-statement',
      name: 'PrivacyCookieStatement',
      component: PrivacyAndCookieStatement
    },
    {
      path: '/terms-of-service',
      name: 'TermsOfService',
      component: TermsOfService
    }
  ]
})

export default router
