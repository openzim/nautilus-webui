<template>
  <tr>
    <th scope="row" class="align-middle">
      <input
        class="form-check-input"
        type="checkbox"
        value=""
        @change.prevent="toggleSelectFile(props.renderId)"
        :checked="props.isSelected"
      />
    </th>
    <td class="align-middle">
      <div v-if="inEditMode || inSingleFileEditMode">
        <input
          :value="metadataFormModal.title"
          class="form-control file-title"
          @input="handleTitleInput"
        />
      </div>
      <div v-else>
        <span class="d-inline-block text-truncate file-title">
          {{ props.clientVisibleFile.file.title }}
        </span>
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
      <div v-if="inEditMode || inSingleFileEditMode">
        <FileMetaDataEditorComponent
          :metadata="metadataFormModal"
          @update-form="updateMetadataForm"
        />
      </div>
      <div v-else>
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
    </td>
    <td class="align-middle">
      <button
        v-show="!inSingleFileEditMode || inEditMode"
        type="button"
        class="btn"
        @click.prevent="deleteFile(props.renderId, props.clientVisibleFile.file)"
      >
        <font-awesome-icon :icon="['fas', 'trash']" />
      </button>
      <button
        v-show="!inEditMode && !inSingleFileEditMode"
        type="button"
        class="btn"
        @click.prevent="inSingleFileEditMode = true"
        :disabled="!props.clientVisibleFile.file.isEditable"
      >
        <font-awesome-icon :icon="['fas', 'file-pen']" />
      </button>
      <div v-show="!inEditMode && inSingleFileEditMode">
        <button type="button" class="btn" @click.prevent="saveMetadata">
          <font-awesome-icon :icon="['fas', 'file-arrow-down']" />
        </button>
        <button type="button" class="btn" @click.prevent="exitEditing">
          <font-awesome-icon :icon="['fas', 'file-excel']" />
        </button>
      </div>
    </td>
  </tr>
</template>

<script setup lang="ts">
import {
  FileStatus,
  humanifyFileSize,
  type ClientVisibleFile,
  type FileMetadataForm,
  type MetadataEditorFormType,
  NautilusFile
} from '@/constants'
import { fromMime } from 'human-filetypes'
import moment from 'moment'
import { computed, ref, watch, type Ref } from 'vue'
import * as bootstrap from 'bootstrap'
import FileMetaDataEditorComponent from '@/components/FileMetaDataEditorComponent.vue'

const props = defineProps<{
  inEditMode: boolean
  isSelected: boolean
  renderId: string
  clientVisibleFile: ClientVisibleFile
}>()
const toolTipsElement: Ref<Element | null> = ref(null)
const upHere = ref(false)
const inSingleFileEditMode = ref(false)
const emit = defineEmits<{
  toggleSelectFile: [key: string]
  deleteFile: [key: string, file: NautilusFile]
  updateFileMetadata: [renderId: string, id: string, metadata: FileMetadataForm]
  updateSingleFileMetadata: [renderId: string, id: string, metadata: FileMetadataForm]
}>()

const metadataFormModal: Ref<FileMetadataForm> = ref({
  title: props.clientVisibleFile.file.title,
  description: props.clientVisibleFile.file.description ?? '',
  authors: props.clientVisibleFile.file.authors?.slice() ?? [],
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

watch(
  () => props.inEditMode,
  () => {
    exitEditing()
  }
)

watch(props.clientVisibleFile, (newValue) => {
  metadataFormModal.value.title = newValue.file.title
  metadataFormModal.value.description = newValue.file.description ?? ''
  metadataFormModal.value.authors = newValue.file.authors?.slice() ?? []
  metadataFormModal.value.filename = newValue.file.filename
})

function handleTitleInput(event: Event) {
  event.preventDefault()
  const target = event.target as HTMLInputElement
  const value = target.value.trim()
  if (value.length != 0) {
    metadataFormModal.value.title = value
  }
  updateFileMetadata()
}

function updateFileMetadata() {
  if (props.inEditMode) {
    emit(
      'updateFileMetadata',
      props.renderId,
      props.clientVisibleFile.file.id,
      metadataFormModal.value
    )
  }
}

async function toggleSelectFile(key: string) {
  emit('toggleSelectFile', key)
}

async function deleteFile(key: string, file: NautilusFile) {
  emit('deleteFile', key, file)
}

async function saveMetadata() {
  emit(
    'updateSingleFileMetadata',
    props.renderId,
    props.clientVisibleFile.file.id,
    metadataFormModal.value
  )
  inSingleFileEditMode.value = false
}

async function updateMetadataForm(newValue: MetadataEditorFormType) {
  metadataFormModal.value.description = newValue.description
  metadataFormModal.value.authors = newValue.authors
  metadataFormModal.value.filename = newValue.filename
  updateFileMetadata()
}

async function exitEditing() {
  metadataFormModal.value.title = props.clientVisibleFile.file.title
  metadataFormModal.value.description = props.clientVisibleFile.file.description ?? ''
  metadataFormModal.value.authors = props.clientVisibleFile.file.authors?.slice() ?? []
  metadataFormModal.value.filename = props.clientVisibleFile.file.filename
  inSingleFileEditMode.value = false
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
