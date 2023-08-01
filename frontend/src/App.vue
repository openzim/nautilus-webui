<script setup lang="ts">
// import { RouterLink, RouterView } from 'vue-router'
// import HelloWorld from './components/HelloWorld.vue'
import TheFooter from './components/TheFooter.vue'
import HomeView from './views/HomeView.vue'
</script>

<template>
  <div class="d-flex flex-column vh-100">
    <div class="flex-shrink-1">
      <HomeView />
    </div>
    <TheFooter />
  </div>
</template>

<style scoped></style>
