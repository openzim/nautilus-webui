<template>
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
</template>

<script setup lang="ts">
import { ref } from 'vue'
const isActive = ref(false)

const emit = defineEmits<{
  dropFilesHandler: [files: FileList]
}>()

function setActive() {
  isActive.value = true
}
function setInactive() {
  isActive.value = false
}
async function dropFiles(event: DragEvent) {
  isActive.value = false
  if (event.dataTransfer?.files == undefined) {
    return
  }
  emit('dropFilesHandler', event.dataTransfer.files)
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
