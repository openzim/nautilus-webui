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
      <div v-if="showEditComponents">
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
      <ToolTipsComponent
        v-if="props.clientVisibleFile.file.status == FileStatus.S3"
        title="File is uploaded"
      >
        <font-awesome-icon class="text-primary fs-5" :icon="['fas', 'check']" />
      </ToolTipsComponent>
      <ToolTipsComponent
        v-else-if="props.clientVisibleFile.file.status == FileStatus.FAILURE"
        :title="props.clientVisibleFile.statusText"
      >
        <font-awesome-icon class="text-danger fs-5" :icon="['fas', 'xmark']" />
      </ToolTipsComponent>
      <ToolTipsComponent
        v-else-if="props.clientVisibleFile.file.status == FileStatus.PROCESSING"
        title="File is processing"
      >
        <div class="spinner-border text-warning" role="status">
          <span class="visually-hidden">Processing...</span>
        </div>
      </ToolTipsComponent>
      <ToolTipsComponent v-else title="File is uploading">
        {{ fileUploadingPercentage }} %
      </ToolTipsComponent>
    </td>
    <td class="align-middle">
      <div v-if="showEditComponents">
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
          {{ isAuthorsAvailable ? `Authors; ` : '' }}
          {{ isDescriptionAvailable ? `Description; ` : '' }}
          <div v-show="upHere" class="card position-absolute bottom-0 start-0 metadata-card">
            <div class="card-body">
              <div class="card-title custom-title">Description:</div>
              <p class="card-text">{{ props.clientVisibleFile.file.description }}</p>
              <div class="card-title custom-title">Authors:</div>
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
        title="Delete File"
      >
        <font-awesome-icon :icon="['fas', 'trash']" />
      </button>
      <button
        v-show="!inEditMode && !inSingleFileEditMode"
        type="button"
        class="btn"
        @click.prevent="inSingleFileEditMode = true"
        :disabled="!props.clientVisibleFile.file.isEditable"
        title="Edit metadata"
      >
        <font-awesome-icon :icon="['fas', 'file-pen']" />
      </button>
      <div v-show="!inEditMode && inSingleFileEditMode">
        <button type="button" class="btn" @click.prevent="saveMetadata" title="Save change">
          <font-awesome-icon :icon="['fas', 'file-arrow-down']" />
        </button>
        <button type="button" class="btn" @click.prevent="exitEditing" title="Discard change">
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
import FileMetaDataEditorComponent from '@/components/FileMetaDataEditorComponent.vue'
import ToolTipsComponent from './ToolTipsComponent.vue'

const props = defineProps<{
  inEditMode: boolean
  isSelected: boolean
  renderId: string
  clientVisibleFile: ClientVisibleFile
}>()
const upHere = ref(false)
const inSingleFileEditMode = ref(false)
const emit = defineEmits<{
  toggleSelectFile: [key: string]
  deleteFile: [key: string, file: NautilusFile]
  updateFileMetadataStatus: [renderId: string, id: string, metadata: FileMetadataForm]
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

const isAuthorsAvailable = computed(
  () =>
    props.clientVisibleFile.file.authors != undefined &&
    props.clientVisibleFile.file.authors!.length != 0
)

const isDescriptionAvailable = computed(
  () =>
    props.clientVisibleFile.file.description != undefined &&
    props.clientVisibleFile.file.description != ''
)

const showEditComponents = computed(
  () => (props.inEditMode || inSingleFileEditMode.value) && props.clientVisibleFile.file.isEditable
)

const fileUploadingPercentage = computed(() => {
  let pc = (props.clientVisibleFile.uploadedSize / props.clientVisibleFile.file.filesize) * 100
  return pc > 100 ? 100 : pc.toFixed(0)
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
  metadataFormModal.value.title = value
  updateFileMetadata()
}

function updateFileMetadata() {
  if (props.inEditMode) {
    emit(
      'updateFileMetadataStatus',
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
