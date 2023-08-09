<template>
  <div
    @dragenter.prevent="setActive"
    @dragover.prevent="setActive"
    @dragleave.prevent="setInactive"
    @drop.prevent="dropFiles"
  >
    <slot :is-active="isActive" />
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/stores'
import { ref } from 'vue'

const isActive = ref(false)
const storeApp = useAppStore()

const emit = defineEmits<{
  dropFilesHandler: [files: FileList, uploadFileSize: number]
}>()

function setActive() {
  isActive.value = true
}

function setInactive() {
  isActive.value = false
}

async function dropFiles(event: DragEvent) {
  isActive.value = false
  let files = event.dataTransfer?.files

  if (files == undefined) {
    return
  }

  let totalSize = 0

  for (const file of files) {
    if (file.size > storeApp.constants.env.NAUTILUS_FILE_QUOTA) {
      storeApp.alertsWarning(`${file.name}'s exceeds the quota`)
      return
    }

    if (file.size + totalSize > storeApp.constants.env.NAUTILUS_PROJECT_QUOTA) {
      storeApp.alertsWarning('Uploading files exceed the quota')
      return
    }

    totalSize += file.size
  }

  emit('dropFilesHandler', files, totalSize)
}
</script>
