<template>
  <tr>
    <th scope="col">
      <input
        class="form-check-input"
        type="checkbox"
        value=""
        :indeterminate="isIndeterminate"
        :checked="isCheckedAll"
        @change.prevent="toggleSelectAllFiles"
      />
    </th>
    <th scope="col">
      <SortButton
        title="Name"
        :increase-function="sortByName"
        :decrease-function="sortByNameReversed"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope=" col">
      <SortButton
        title="File Size"
        :increase-function="sortBySizeDescending"
        :decrease-function="sortBySizeAscending"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope="col">
      <SortButton
        title="Kind"
        :increase-function="sortByKindNameReversed"
        :decrease-function="sortByKindName"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope="col">
      <SortButton
        title="Date Uploaded"
        :increase-function="sortByUploadedDateDescending"
        :decrease-function="sortByUploadedDateAscending"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope="col">
      <SortButton
        title="Status"
        :increase-function="sortByStatusNameReversed"
        :decrease-function="sortByStatusName"
        @update-compare-function="updateCompareFunction"
      />
    </th>
    <th scope="align-middle">Metadata</th>
    <th scope="col">
      <button
        type="button"
        class="btn border-0"
        :disabled="isDisableDeleteButton"
        @click.prevent="emit('deleteSelectedFiles')"
      >
        <font-awesome-icon :icon="['fas', 'trash']" />
      </button>
    </th>
  </tr>
</template>

<script setup lang="ts">
import type { ClientVisibleFile } from '@/constants'
import SortButton from './SortButton.vue'
import type { CompareFunctionType } from '@/constants'
import { computed } from 'vue'

const props = defineProps<{
  selectedFiles: Map<string, boolean>
  files: Map<string, ClientVisibleFile>
}>()

const emit = defineEmits<{
  updateSelectFiles: [newValue: Map<string, boolean>]
  deleteSelectedFiles: []
  updateCompareFunction: [
    newFunction: (a: [string, ClientVisibleFile], b: [string, ClientVisibleFile]) => number
  ]
}>()

const isIndeterminate = computed(
  () => props.selectedFiles.size != 0 && props.selectedFiles.size < props.files.size
)
const isCheckedAll = computed(
  () => props.selectedFiles.size != 0 && props.selectedFiles.size == props.files.size
)
const isDisableDeleteButton = computed(() => props.selectedFiles.size == 0)

/** Start to define compare functions **/
const sortByName: CompareFunctionType = (a, b) => (a[1].file.title > b[1].file.title ? 1 : -1)
const sortByNameReversed: CompareFunctionType = (a, b) =>
  a[1].file.title < b[1].file.title ? 1 : -1

const sortBySizeAscending: CompareFunctionType = (a, b) =>
  a[1].file.filesize > b[1].file.filesize ? 1 : -1
const sortBySizeDescending: CompareFunctionType = (a, b) =>
  a[1].file.filesize < b[1].file.filesize ? 1 : -1

const sortByKindName: CompareFunctionType = (a, b) => (a[1].file.type > b[1].file.type ? 1 : -1)
const sortByKindNameReversed: CompareFunctionType = (a, b) =>
  a[1].file.type < b[1].file.type ? 1 : -1

const sortByUploadedDateAscending: CompareFunctionType = (a, b) =>
  a[1].file.uploaded_on > b[1].file.uploaded_on ? 1 : -1
const sortByUploadedDateDescending: CompareFunctionType = (a, b) =>
  a[1].file.uploaded_on < b[1].file.uploaded_on ? 1 : -1

const sortByStatusName: CompareFunctionType = (a, b) =>
  a[1].file.status > b[1].file.status ? 1 : -1
const sortByStatusNameReversed: CompareFunctionType = (a, b) =>
  a[1].file.status < b[1].file.status ? 1 : -1

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
