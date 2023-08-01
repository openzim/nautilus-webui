<script setup lang="ts">
import FooterComponetns from './components/FooterComponents.vue'
</script>

<template>
  <div class="d-flex flex-column vh-100">
    <div class="flex-shrink-1">
      <RouterView />
    </div>
    <FooterComponetns />
  </div>
</template>

<style scoped></style>
