<template>
  <div class="container-fluid vh-100">
    <div class="row">
      <div class="col col-2 sticky-top sidebar">
        <SideBarComponent />
      </div>
      <div class="col content d-flex flex-column justify-content-between overflow-hidden">
        <div>
          <ProjectView v-if="hasValidProjectId" />
        </div>
        <FooterComponent />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SideBarComponent from '@/components/SideBarComponent.vue'
import FooterComponent from '@/components/FooterComponent.vue'
import ProjectView from './ProjectView.vue'
import { useProjectStore } from '@/stores/stores'
import { computed } from 'vue'

defineProps({ page: String })
const storeProject = useProjectStore()
const hasValidProjectId = computed(() => storeProject.lastProjectId != null)
</script>

<style scoped>
.collection-container {
  height: 100vh;
}

.sidebar {
  background-color: var(--main-color);
  height: 100vh;
  width: 33%;
  max-width: 25em;
}

.content {
  min-height: 100vh;
}
</style>
