<template>
  <div class="d-flex flex-column vh-100">
    <div class="flex-shrink-1">
      <div class="mt-5">
        <SloganComponent />
      </div>
      <div class="mt-5">
        <Suspense>
          <div class="container">
            <h2>404 Error: Not Found</h2>
            <p>We could not match your request with a valid document.</p>
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
import FrequentlyAskedQuestions from '@/components/FrequentlyAskedQuestions.vue'
import DragToStartProjectComponent from '@/components/DragToStartProjectComponent.vue'
import StatementsComponent from '@/components/StatementsComponent.vue'
</script>
