<template>
  <tr>
    <th scope="row" class="align-middle">
      <input
        class="form-check-input"
        type="checkbox"
        value=""
        @change.prevent="toggleSelectFile(props.renderKey)"
        :checked="props.isSelected"
      />
    </th>
    <td class="align-middle">
      <div v-if="!isEditMode">
        <span class="d-inline-block text-truncate file-title">
          {{ props.clientVisibleFile.file.title }}
        </span>
      </div>
      <div v-else>
        <input v-model="metaDataFormModal.title" class="form-control file-title" />
      </div>
    </td>
    <td class="align-middle">
      {{ humanifyFileSize(props.clientVisibleFile.file.filesize) }}
    </td>
    <td class="align-middle">
      {{ fromMime(props.clientVisibleFile.file.type) }}
    </td>
    <td class="align-middle">
      {{ fileUploadedDate }}
    </td>
    <td class="align-middle ps-4">
      <!-- TODO: Once S3 uploading part is finished, we need to change this part to show better progress. -->
      <div
        v-if="props.clientVisibleFile.file.status == FileStatus.UPLOADING"
        class="spinner-border text-secondary"
        role="status"
      >
        <span class="visually-hidden">Loading...</span>
      </div>
      <span
        v-else-if="props.clientVisibleFile.file.status == FileStatus.FAILURE"
        data-bs-toggle="tooltip"
        :data-bs-title="props.clientVisibleFile.statusText"
        ref="toolTipsElement"
      >
        <font-awesome-icon class="text-danger fs-5" :icon="['fas', 'xmark']" />
      </span>
      <span v-else>
        <font-awesome-icon class="text-primary fs-5" :icon="['fas', 'check']" />
      </span>
    </td>
    <td class="align-middle">
      <div v-if="!isEditMode">
        <div
          class="position-relative"
          @mouseover.prevent="upHere = true"
          @mouseleave.prevent="upHere = false"
        >
          {{
            props.clientVisibleFile.file.authors != undefined &&
            props.clientVisibleFile.file.authors!.length != 0
              ? `Authors; `
              : ''
          }}
          {{
            props.clientVisibleFile.file.description != undefined &&
            props.clientVisibleFile.file.description != ''
              ? `Description; `
              : ''
          }}
          <div v-show="upHere" class="card position-absolute bottom-0 start-0 metadata-card">
            <div class="card-body">
              <div class="card-title custom-title">Description:</div>
              <p class="card-text">{{ props.clientVisibleFile.file.description }}</p>
              <div class="card-title custom-title">Auhtors:</div>
              <p class="card-text">
                {{ authors }}
              </p>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <FileMetaDataEditorComponent
          :metadata="metaDataFormModal"
          @update-form="updateMetadataForm"
        />
      </div>
    </td>
    <td class="align-middle">
      <div v-if="!isEditMode">
        <button
          type="button"
          class="btn"
          @click.prevent="deleteFile(props.renderKey, props.clientVisibleFile.file)"
        >
          <font-awesome-icon :icon="['fas', 'trash']" />
        </button>
        <button
          type="button"
          class="btn"
          @click.prevent="isEditMode = true"
          :disabled="!props.clientVisibleFile.file.isEditable"
        >
          <font-awesome-icon :icon="['fas', 'file-pen']" />
        </button>
      </div>
      <div v-else>
        <button type="button" class="btn" @click.prevent="saveMetadata">
          <font-awesome-icon :icon="['fas', 'file-arrow-down']" />
        </button>
      </div>
    </td>
  </tr>
</template>

<script setup lang="ts">
import {
  FileStatus,
  humanifyFileSize,
  FileClass,
  type ClientVisibleFile,
  type FileMetadataForm,
  type MetadataEditorFormType
} from '@/constants'
import { fromMime } from 'human-filetypes'
import moment from 'moment'
import { computed, ref, watch, type Ref } from 'vue'
import * as bootstrap from 'bootstrap'
import FileMetaDataEditorComponent from '@/components/FileMetaDataEditorComponent.vue'

const props = defineProps<{
  isSelected: boolean
  renderKey: string
  clientVisibleFile: ClientVisibleFile
}>()
const toolTipsElement: Ref<Element | null> = ref(null)
const upHere = ref(false)
const emit = defineEmits<{
  toggleSelectFile: [key: string]
  deleteFile: [key: string, file: FileClass]
  updateFileMetadata: [id: string, metadata: FileMetadataForm]
}>()
const isEditMode = ref(false)

const metaDataFormModal: Ref<FileMetadataForm> = ref({
  title: props.clientVisibleFile.file.title,
  description: props.clientVisibleFile.file.description ?? '',
  authors: props.clientVisibleFile.file.authors ?? [],
  filename: props.clientVisibleFile.file.filename
})

const fileUploadedDate = computed(() =>
  moment.utc(props.clientVisibleFile.file.uploaded_on).local().format('MMM DD HH:mm')
)
const authors = computed(() =>
  props.clientVisibleFile.file.authors?.reduce((prev, author) => prev + author + ',', '')
)

watch(toolTipsElement, (newValue) => {
  if (newValue != null) {
    new bootstrap.Tooltip(newValue)
  }
})

async function toggleSelectFile(key: string) {
  emit('toggleSelectFile', key)
}

async function deleteFile(key: string, file: FileClass) {
  emit('deleteFile', key, file)
}

async function saveMetadata() {
  isEditMode.value = false
  emit('updateFileMetadata', props.clientVisibleFile.file.id, metaDataFormModal.value)
}

async function updateMetadataForm(newValue: MetadataEditorFormType) {
  metaDataFormModal.value.description = newValue.description
  metaDataFormModal.value.authors = newValue.authors
  metaDataFormModal.value.filename = newValue.filename
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

.file-title {
  max-width: 12em;
}
</style>
