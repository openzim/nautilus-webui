<template>
  <div class="mt-5">
    <SloganComponent />
  </div>
  <div class="mt-5">
    <Suspense>
      <DragToStartProjectComponent />
    </Suspense>
  </div>
</template>

<script setup lang="ts">
import SloganComponent from '@/components/SloganComponent.vue'
import DragToStartProjectComponent from '@/components/DragToStartProjectComponent.vue'
</script>
