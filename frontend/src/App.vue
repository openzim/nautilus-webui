<template>
  <div class="d-flex flex-column vh-100" v-if="isReady">
    <div class="flex-shrink-1">
      <Suspense>
        <RouterView />
      </Suspense>
    </div>
    <FooterComponent />
  </div>
  <AlertsComponentVue />
</template>

<script setup lang="ts">
import AlertsComponentVue from './components/AlertsComponent.vue'
import FooterComponent from './components/FooterComponent.vue'
import { onMounted, ref } from 'vue'
import { useAppStore } from './stores/stores'

const storeApp = useAppStore()
const isReady = ref(false)
onMounted(async () => {
  await storeApp.initConstants()
  isReady.value = true
})
</script>
