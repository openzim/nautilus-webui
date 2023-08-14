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
    <th scope="col">
      <SortButton
        title="Name"
        :increase-function="increaseByName"
        :decrease-function="decreaseByName"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope=" col">
      <SortButton
        title="File Size"
        :increase-function="increaseBySize"
        :decrease-function="decreaseBySize"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope="col">
      <SortButton
        title="Kind"
        :increase-function="increaseByKind"
        :decrease-function="decreaseByKind"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope="col">
      <SortButton
        title="Date Uploaded"
        :increase-function="increaseByUploadedDate"
        :decrease-function="decreaseByUploadedDate"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope="col">
      <SortButton
        title="Status"
        :increase-function="increaseByStatus"
        :decrease-function="decreaseByStatus"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope="align-middle">Metadata</th>
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
import SortButton from './SortButton.vue'
import type { CompareFunctionType } from '@/constants'

const props = defineProps<{
  selectedFiles: Map<string, boolean>
  files: Map<string, RenderFile>
}>()

const emit = defineEmits<{
  updateSelectFiles: [newValue: Map<string, boolean>]
  deleteSelectedFiles: []
  updateCompareFunction: [newFunction: (a: [string, RenderFile], b: [string, RenderFile]) => number]
}>()

/** Start to define compare functions **/
const increaseByName: CompareFunctionType = (a, b) => (a[1].file.title > b[1].file.title ? 1 : -1)
const decreaseByName: CompareFunctionType = (a, b) => (a[1].file.title < b[1].file.title ? 1 : -1)

const increaseBySize: CompareFunctionType = (a, b) =>
  a[1].file.filesize < b[1].file.filesize ? 1 : -1
const decreaseBySize: CompareFunctionType = (a, b) =>
  a[1].file.filesize > b[1].file.filesize ? 1 : -1

const increaseByKind: CompareFunctionType = (a, b) => (a[1].file.type < b[1].file.type ? 1 : -1)
const decreaseByKind: CompareFunctionType = (a, b) => (a[1].file.type > b[1].file.type ? 1 : -1)

const increaseByUploadedDate: CompareFunctionType = (a, b) =>
  a[1].file.uploaded_on < b[1].file.uploaded_on ? 1 : -1
const decreaseByUploadedDate: CompareFunctionType = (a, b) =>
  a[1].file.uploaded_on > b[1].file.uploaded_on ? 1 : -1

const increaseByStatus: CompareFunctionType = (a, b) =>
  a[1].file.status < b[1].file.status ? 1 : -1
const decreaseByStatus: CompareFunctionType = (a, b) =>
  a[1].file.status > b[1].file.status ? 1 : -1

/** End of definition**/

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

function updateCompareFunction(newValue: CompareFunctionType) {
  emit('updateCompareFunction', newValue)
}
</script>
