<template>
  <div class="d-flex flex-column vh-100">
    <div class="flex-shrink-1">
      <RouterView />
    </div>
    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import FooterComponent from './components/FooterComponent.vue'
import router from './router'
axios.get(`${import.meta.env.VITE_API_URL}/projects`).then(() => {
  router.push({ path: '/project' })
})
</script>
