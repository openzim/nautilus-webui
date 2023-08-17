import PrivacyAndCookieStatement from '@/views/PrivacyAndCookieStatement.vue'
import StartView from '@/views/StartView.vue'
import TermsOfService from '@/views/TermsOfService.vue'
import CollectionView from '@/views/CollectionView.vue'
import { createRouter, createWebHistory } from 'vue-router'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'start',
      component: StartView
    },
    {
      path: '/collection',
      name: 'collection',
      component: CollectionView
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
