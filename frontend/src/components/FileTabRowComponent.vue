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
    <td>{{ props.renderFile.file.filename }}</td>
    <td>{{ humanifyFileSize(props.renderFile.file.filesize) }}</td>
    <td>{{ fromMime(props.renderFile.file.type) }}</td>
    <td>{{ new Date(props.renderFile.file.uploaded_on).toLocaleString() }}</td>
    <td>
      <div
        class="progress"
        role="progressbar"
        v-if="props.renderFile.file.status == FileStatus.UPLOADING"
      >
        <div
          class="progress-bar"
          :style="{
            width: (props.renderFile.uploadedSize / props.renderFile.file.filesize) * 100 + '%'
          }"
        />
      </div>
      <div v-else>
        {{ props.renderFile.file.status }}
      </div>
    </td>
    <td>
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
    <td>
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
