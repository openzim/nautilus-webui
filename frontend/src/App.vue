<template>
  <Suspense v-if="isReady">
    <RouterView />
  </Suspense>
  <AlertsComponentVue />
</template>

<script setup lang="ts">
import AlertsComponentVue from './components/AlertsComponent.vue'
import { onMounted, ref } from 'vue'
import { useAppStore } from './stores/stores'

const storeApp = useAppStore()
const isReady = ref(false)
onMounted(async () => {
  await storeApp.initConstants()
  isReady.value = true
})
</script>
