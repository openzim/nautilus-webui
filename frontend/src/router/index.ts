import CollectionsView from '@/views/CollectionsView.vue'
import StartView from '@/views/StartView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import NotFoundView from '@/views/NotFoundView.vue'
import StaticStartView from '@/views/StaticStartView.vue'
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
      component: StaticStartView,
      props: { page: 'privacy', showTitle: true }
    },
    {
      path: '/faq',
      name: 'faq',
      component: StaticStartView,
      props: { page: 'faq', showTitle: true }
    },
    {
      path: '/terms-of-service',
      name: 'TermsOfService',
      component: StaticStartView,
      props: { page: 'tos', showTitle: true }
    },
    {
      path: '/contact',
      name: 'contact',
      component: StaticStartView,
      props: { page: 'contact', showTitle: true }
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
