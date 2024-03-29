import PrivacyAndCookieStatement from '@/views/PrivacyAndCookieStatement.vue'
import StartView from '@/views/StartView.vue'
import TermsOfService from '@/views/TermsOfService.vue'
import CollectionsView from '@/views/CollectionsView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import FrequentlyAskedQuestions from '@/components/FrequentlyAskedQuestions.vue'
import ContactPage from '@/components/ContactPage.vue'
import NotFoundView from '@/views/NotFoundView.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/collections',
      name: 'collections',
      component: CollectionsView
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
    },
    {
      path: '/faq',
      name: 'faq',
      component: FrequentlyAskedQuestions
    },
    {
      path: '/contact',
      name: 'contact',
      component: ContactPage
    },
    {
      path: '/',
      name: 'start',
      component: StartView
    },
    {
      path: '/:pathMatch(.*)*',
      name: '404',
      component: NotFoundView
    }
  ]
})

export default router
