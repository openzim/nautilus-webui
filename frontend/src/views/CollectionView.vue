<template>
  <div class="container-fluid vh-100">
    <div class="row">
      <div class="col col-3 sticky-top test">
        <SideBarComponent />
      </div>
      <div class="col content d-flex flex-column justify-content-between">
        <div>
          <ProjectView />
        </div>
        <FooterComponent />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SideBarComponent from '@/components/SideBarComponent.vue'
import FooterComponent from '@/components/FooterComponent.vue'
import ProjectView from './ProjectView.vue';
</script>

<style scoped>
.collection-container {
  height: 100vh;
}

.test {
  background-color: var(--main-color);
  height: 100vh;
}

.test2 {
  min-height: 100vh;
}

.content {

  min-height: 100vh;
}
</style>
