<template>
  <div class="mt-5">
    <SloganComponent />
  </div>
  <div class="mt-5">
    <ProjectView :project="undefined" />
  </div>
  <div class="mt-5">
    <FrequentlyAskedQuestions />
  </div>
</template>

<script setup lang="ts">
import SloganComponent from '@/components/SloganComponent.vue'
import FrequentlyAskedQuestions from '@/components/FrequentlyAskedQuestions.vue'
import ProjectView from '@/views/ProjectView.vue'
</script>
