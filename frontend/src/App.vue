<template>
  <Suspense v-if="isReady">
    <RouterView />
  </Suspense>
  <AlertsComponentVue />
  <ModalComponent />
</template>

<script setup lang="ts">
import AlertsComponentVue from './components/AlertsComponent.vue'
import ModalComponent from './components/ModalComponent.vue'
import { onMounted, ref } from 'vue'
import { useAppStore } from './stores/stores'

const storeApp = useAppStore()
const isReady = ref(false)
onMounted(async () => {
  await storeApp.initConstants()
  isReady.value = true
})
</script>
