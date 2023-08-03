<template>
  <div class="container">
    <div class="d-flex justify-content-md-center">
      <div
        class="card border-3 border-3 rounded-3 drop"
        :data-active="isActive"
        @dragenter.prevent="setActive"
        @dragover.prevent="setActive"
        @dragleave.prevent="setInactive"
        @drop.prevent="dropFiles"
        :class="{ 'bg-light': isActive }"
      >
        <div class="card-body d-flex justify-content-center align-items-center">
          <h3 class="card-title">Drop File to Start!</h3>
        </div>
      </div>
    </div>
    <div class="d-flex justify-content-md-center text-secondary">
      <p>
        Agree to our
        <RouterLink to="/privacy-and-cookie-statement"> Terms of Service </RouterLink> and
        <RouterLink to="/terms-of-service"> Privacy & Cookie Statement</RouterLink>.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const isActive = ref(false)

const emit = defineEmits<{
  dropFilesHandler: [event: DragEvent]
}>()

function setActive() {
  isActive.value = true
}
function setInactive() {
  isActive.value = false
}
async function dropFiles(event: DragEvent) {
  isActive.value = false
  emit('dropFilesHandler', event)
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
