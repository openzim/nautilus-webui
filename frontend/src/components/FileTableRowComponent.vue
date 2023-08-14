<template>
  <tr>
    <th scope="row">
      <input
        class="form-check-input"
        type="checkbox"
        value=""
        @change.prevent="toggleSelectFile(props.renderKey)"
        :checked="props.isSelected"
      />
    </th>
    <td class="align-middle">
      {{ props.renderFile.file.filename }}
    </td>
    <td class="align-middle">
      {{ humanifyFileSize(props.renderFile.file.filesize) }}
    </td>
    <td class="align-middle">
      {{ fromMime(props.renderFile.file.type) }}
    </td>
    <td class="align-middle">
      {{ moment.utc(props.renderFile.file.uploaded_on).local().format('MMM DD HH:mm') }}
    </td>
    <td class="align-middle ps-4">
      <div
        v-if="props.renderFile.file.status == FileStatus.UPLOADING"
        class="spinner-border text-secondary"
        role="status"
      >
        <span class="visually-hidden">Loading...</span>
      </div>
      <font-awesome-icon
        class="text-danger fs-5"
        v-else-if="props.renderFile.statusCode != undefined"
        :icon="['fas', 'xmark']"
      />
      <font-awesome-icon class="text-primary fs-5" v-else :icon="['fas', 'check']" />
    </td>
    <td class="align-middle">
      <div
        class="position-relative"
        @mouseover.prevent="upHere = true"
        @mouseleave.prevent="upHere = false"
      >
        {{ props.renderFile.file.authors != undefined ? `Authors; ` : '' }}
        {{ props.renderFile.file.description != undefined ? `Description; ` : '' }}
        <div v-show="upHere" class="card position-absolute bottom-0 start-0 metadata-card">
          <div class="card-body">
            <div class="card-title custom-title">Description:</div>
            <p class="card-text">{{ props.renderFile.file.description }}</p>
            <div class="card-title custom-title">Auhtors:</div>
            <p class="card-text">
              {{ props.renderFile.file.authors?.reduce((prev, author) => prev + author + ',', '') }}
            </p>
          </div>
        </div>
      </div>
    </td>
    <td class="align-middle">
      <button
        type="button"
        class="btn"
        @click.prevent="deleteFile(props.renderKey, props.renderFile.file)"
      >
        <font-awesome-icon :icon="['fas', 'trash']" />
      </button>
      <button type="button" class="btn" v-if="props.showEditButton">
        <font-awesome-icon :icon="['fas', 'file-pen']" />
      </button>
    </td>
  </tr>
</template>

<script setup lang="ts">
import { FileStatus, humanifyFileSize, type File, type RenderFile } from '@/constants'
import { fromMime } from 'human-filetypes'
import moment from 'moment'
import { ref } from 'vue'

const props = defineProps<{
  isSelected: boolean
  renderKey: string
  renderFile: RenderFile
  showEditButton: boolean
}>()
const upHere = ref(false)
const emit = defineEmits<{
  toggleSelectFile: [key: string]
  deleteFile: [key: string, file: File]
}>()

async function toggleSelectFile(key: string) {
  emit('toggleSelectFile', key)
}

async function deleteFile(key: string, file: File) {
  emit('deleteFile', key, file)
}
</script>

<style scoped>
.metadata-card {
  max-width: 20em;
  transform: translate(0, 100%);
  z-index: 2000;
}

.custom-title {
  color: var(--main-color);
}
</style>