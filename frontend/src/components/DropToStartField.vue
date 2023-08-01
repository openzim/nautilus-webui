<template>
  <TheSlogan />
  <div class="container">
    <div class="row justify-content-md-center">
      <div
        class="card border-3 border-3 rounded-3 drop"
        :data-active="isActive"
        @dragenter.prevent="setActive"
        @dragover.prevent="setActive"
        @dragleave.prevent="setInactive"
        :class="{ 'bg-light': isActive }"
      >
        <div class="card-body d-flex justify-content-center align-items-center">
          <h3 class="card-title">Drop File to Start!</h3>
        </div>
      </div>
    </div>
    <div class="row justify-content-md-center text-secondary">
      Agree to our Terms of Service and Privacy & Cookie Statement.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const isActive = ref(false)
function setActive() {
  isActive.value = true
}
function setInactive() {
  isActive.value = false
}
</script>

<style scoped>
.drop {
  width: 25em;
  height: 10em;
  border-style: dashed;
  border-color: var(--main-color);
  color: var(--main-color);
}

.isActive {
  background-color: var(--main-color);
  opacity: 0.6;
}
</style>
