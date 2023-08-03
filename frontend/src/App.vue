<template>
  <div class="d-flex flex-column vh-100">
    <div class="flex-shrink-1">
      <RouterView />
    </div>
    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import FooterComponent from './components/FooterComponent.vue'
</script>
