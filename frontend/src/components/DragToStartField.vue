<template>
  <div class="d-flex justify-content-md-center">
    <UploadFilesComponent @drop-files-handler="dropFiles" @update-is-active="updateIsActive">
      <div
        class="card border-3 rounded-3 drop"
        :data-active="isActive"
        :class="{ 'bg-light': isActive }"
      >
        <div class="card-body d-flex justify-content-center align-items-center">
          <h3 class="card-title">Drop File to Start!</h3>
        </div>
      </div>
    </UploadFilesComponent>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UploadFilesComponent from './UploadFilesComponent.vue'
const isActive = ref(false)

function updateIsActive(newValue: boolean) {
  isActive.value = newValue
}
const emit = defineEmits<{
  dropFilesHandler: [files: FileList, uploadFileSize: number]
}>()

async function dropFiles(files: FileList, uploadFileSize: number) {
  emit('dropFilesHandler', files, uploadFileSize)
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
</style>
