<template>
  <div class="mt-5">
    <SloganComponent />
  </div>
  <div class="mt-5">
    <Suspense>
      <div class="container">
        <DragToStartProjectComponent />
        <StatementsComponent />
      </div>
    </Suspense>
  </div>
  <div class="mt-5">
    <FrequentlyAskedQuestions />
  </div>
</template>

<script setup lang="ts">
import SloganComponent from '@/components/SloganComponent.vue'
import FrequentlyAskedQuestions from '@/components/FrequentlyAskedQuestions.vue'
import DragToStartProjectComponent from '@/components/DragToStartProjectComponent.vue'
import StatementsComponent from '@/components/StatementsComponent.vue'
</script>
