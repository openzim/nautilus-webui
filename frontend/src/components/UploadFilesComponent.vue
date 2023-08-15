<template>
  <div @dragenter.prevent="setActive" @dragover.prevent="setActive" @dragleave.prevent="setInactive"
    @drop.prevent="dropFiles">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/stores'

const storeApp = useAppStore()

const emit = defineEmits<{
  dropFilesHandler: [files: FileList, uploadFileSize: number]
  updateIsActive: [newValue: boolean]
}>()

function setActive() {
  emit('updateIsActive', true)
}

function setInactive() {
  emit('updateIsActive', false)
}

async function dropFiles(event: DragEvent) {
  emit('updateIsActive', false)
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

    if (file.size == 0) {
      storeApp.alertsWarning("Empty files cannot be uploaded")
      return
    }

    if (file.type == '') {
      storeApp.alertsWarning('Folders and files without extension cannot be uploaded')
      return
    }

    totalSize += file.size
  }

  emit('dropFilesHandler', files, totalSize)
}
</script>
