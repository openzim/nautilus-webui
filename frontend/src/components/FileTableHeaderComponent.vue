<template>
  <tr>
    <th scope="col">
      <input
        class="form-check-input"
        type="checkbox"
        value=""
        :indeterminate="
          props.selectedFiles.size != 0 && props.selectedFiles.size < props.files.size
        "
        :checked="selectedFiles.size != 0 && selectedFiles.size == props.files.size"
        @change.prevent="toggleSelectAllFiles"
      />
    </th>
    <th scope="col">Name</th>
    <th scope="col">File Size</th>
    <th scope="col">File Type</th>
    <th scope="col">Uploaded On</th>
    <th scope="col">Status</th>
    <th scope="col">Metadata</th>
    <th scope="col">
      <button
        type="button"
        class="btn"
        :disabled="selectedFiles.size == 0"
        @click.prevent="emit('deleteSelectedFiles')"
      >
        <font-awesome-icon :icon="['fas', 'trash']" />
      </button>
    </th>
  </tr>
</template>

<script setup lang="ts">
import type { RenderFile } from '@/constants'

const props = defineProps<{
  selectedFiles: Map<string, boolean>
  files: Map<string, RenderFile>
}>()

const emit = defineEmits<{
  updateSelectFiles: [newValue: Map<string, boolean>]
  deleteSelectedFiles: []
  updateCompareFunction: [newFunction: (a: [string, RenderFile], b: [string, RenderFile]) => number]
}>()

async function toggleSelectAllFiles() {
  let newSelectedFiles: Map<string, boolean> = new Map()
  if (props.selectedFiles.size < props.files.size) {
    props.files.forEach((_, key) => {
      newSelectedFiles.set(key, true)
    })
  } else {
    newSelectedFiles.clear()
  }
  emit('updateSelectFiles', newSelectedFiles)
}
</script>
