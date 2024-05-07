<template>
  <div class="d-flex flex-column vh-100">
    <div class="flex-shrink-1">
      <div class="mt-5">
        <SloganComponent />
      </div>
      <div class="mt-5">
        <Suspense>
          <div class="container">
            <TermsOfService v-if="page == 'tos'" :show-title="showTitle" />
            <PrivacyAndCookieStatement v-else-if="page == 'privacy'" :show-title="showTitle" />
            <FrequentlyAskedQuestions v-else-if="page == 'faq'" :show-title="showTitle" />
            <ContactPage v-else-if="page == 'contact'" :show-title="showTitle" />
            <p v-else>–</p>
          </div>
        </Suspense>
      </div>
    </div>
    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import FooterComponent from '@/components/FooterComponent.vue'
import SloganComponent from '@/components/SloganComponent.vue'
import TermsOfService from '@/components/TermsOfService.vue'
import PrivacyAndCookieStatement from '@/components/PrivacyAndCookieStatement.vue'
import FrequentlyAskedQuestions from '@/components/FrequentlyAskedQuestions.vue'
import ContactPage from '@/components/ContactPage.vue'

defineProps({page: String, showTitle: Boolean})
</script>

<style type="text/css">
a, a:active, a:visited { color: var(--main-color); text-decoration: none; }
</style>
