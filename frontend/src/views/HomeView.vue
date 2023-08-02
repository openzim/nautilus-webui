<template>
  <div class="mt-5">
    <SloganComponent />
    <div class="mt-5">
      <DropToStartField />
    </div>
    <div class="mt-5">
      <FrequentlyAskedQuestions />
    </div>
  </div>
</template>

<script setup lang="ts">
import SloganComponent from '@/components/SloganComponent.vue'
import DropToStartField from '@/components/DropToStartField.vue'
import FrequentlyAskedQuestions from '@/components/FrequentlyAskedQuestions.vue'
</script>
