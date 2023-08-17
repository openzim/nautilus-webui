<template>
  <div class="card m-5" :class="{ border: isActive, 'border-3': isActive, 'drag-active': isActive }">
    <div class="card-body">
      <div class="card-title d-flex justify-content-between align-items-baseline" :class="{ 'border-bottom': isShowed }">
        <h4>
          <button type="button" class="btn text-secondary" @click.prevent="isShowed = !isShowed">
            <font-awesome-icon v-if="isShowed" :icon="['fas', 'minus']" />
            <font-awesome-icon v-else :icon="['fas', 'angle-down']" />
          </button>
          <span style="color: var(--main-color)">Upload Files:</span>
        </h4>
        <div class="align-bottom fw-bold text-secondary">
          {{ humanifyFileSize(totalSize) }}
          /
          {{ humanifyFileSize(storeApp.constants.env.NAUTILUS_PROJECT_QUOTA) }}
        </div>
      </div>
      <UploadFilesComponent @drop-files-handler="dropFilesHandler" @update-is-active="updateIsActive" v-show="isShowed">
        <div>
          <div class="d-flex flex-row-reverse">
            <div class="btn-group btn-group-sm custom-btn-outline-primary" role="group">
              <input type="radio" class="btn-check" name="btnradio" id="edit" autocomplete="off"
                @change="isEditMode = true" :checked="isEditMode" />
              <label class="btn btn-outline-primary" for="edit">Edit</label>

              <input type="radio" class="btn-check" name="btnradio" id="upload" autocomplete="off"
                @change="isEditMode = false" :checked="!isEditMode" />
              <label class="btn btn-outline-primary" for="upload">Upload</label>
            </div>
          </div>
          <table class="table">
            <thead>
              <FileTableHeaderComponent :selected-files="selectedFiles" :files="files"
                @update-select-files="updateSelectFiles" @delete-selected-files="deleteSelectedFiles"
                @update-compare-function="updateCompareFunction" />
            </thead>
            <tbody>
              <FileTableRowComponent v-for="[key, file] in sortedFiles" :key="key" :render-key="key"
                :client-visible-file="file" :is-selected="selectedFiles.has(key)" :show-edit-button="isEditMode"
                @toggle-select-file="toggleSelectFile" @delete-file="deleteSingleFile" />
            </tbody>
          </table>
          <div class="drag-field d-flex justify-content-center align-items-center" v-if="files.size <= 10">
            <h4 style="color: var(--main-color); opacity: 0.6">Drag Files to here</h4>
          </div>
        </div>
      </UploadFilesComponent>
    </div>
    <ModalComponent title="Are you sure you want to delete:" primary-button-title="Delete" secondary-button-title="Close"
      @click-primary-button="deleteFiles" @click-secondary-button="toBeDeletedFiles.clear()" ref="deletionModal">
      <ul>
        <li v-for="[key, file] in toBeDeletedFiles" :key="key">
          {{ file.filename }}
        </li>
      </ul>
    </ModalComponent>
  </div>
</template>
<script setup lang="ts">
import UploadFilesComponent from '@/components/UploadFilesComponent.vue'
import FileTableRowComponent from '@/components/FileTableRowComponent.vue'
import FileTableHeaderComponent from '@/components/FileTableHeaderComponent.vue'
import ModalComponent from '@/components/ModalComponent.vue'
import {
  FileStatus,
  type File,
  type ClientVisibleFile,
  humanifyFileSize,
  type CompareFunctionType
} from '@/constants'
import { useAppStore, useProjectIdStore, useInitialFilesStore } from '@/stores/stores'
import axios from 'axios'
import { ref, type Ref, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'

const isActive = ref(false)
const isEditMode = ref(false)
const isShowed = ref(true)
const storeApp = useAppStore()
const storeProjectId = useProjectIdStore()
const { projectId } = storeToRefs(storeProjectId)
const storeInitialFileStore = useInitialFilesStore()
const files: Ref<Map<string, ClientVisibleFile>> = ref(new Map())
const selectedFiles: Ref<Map<string, boolean>> = ref(new Map())
const totalSize = computed(() =>
  Array.from(files.value.values()).reduce((pre, element) => pre + element.file.filesize, 0)
)
const deletionModal: Ref<InstanceType<typeof ModalComponent> | null> = ref(null)
const toBeDeletedFiles: Ref<Map<string, File>> = ref(new Map())
const compareFunction: Ref<CompareFunctionType> = ref((a, b) =>
  a[1].file.uploaded_on > b[1].file.uploaded_on ? 1 : -1
)
const sortedFiles: Ref<Map<string, ClientVisibleFile>> = computed(() =>
  sortFiles(files.value, compareFunction.value)
)

watch(projectId, async () => {
  files.value.clear()
  const apiFiles = await getAllFiles(storeProjectId.projectId)
  apiFiles.forEach((item) => files.value.set(item.id, { file: item, uploadedSize: item.filesize }))
  console.log("HHHHH")
})

if (storeInitialFileStore.initialFiles.length == 0) {
  const apiFiles = await getAllFiles(storeProjectId.projectId)
  apiFiles.forEach((item) => files.value.set(item.id, { file: item, uploadedSize: item.filesize }))
} else {
  await uploadFiles(storeInitialFileStore.initialFiles)
}

function sortFiles(
  files: Map<string, ClientVisibleFile>,
  compareFunction: CompareFunctionType
): Map<string, ClientVisibleFile> {
  return new Map([...files.entries()].sort(compareFunction))
}

function updateIsActive(newValue: boolean) {
  isActive.value = newValue
}

async function getAllFiles(projectId: string | null) {
  var result: File[] = []
  if (projectId == null) {
    return result
  }
  try {
    const reponse = await storeApp.axiosInstance.get<File[]>(`/projects/${projectId}/files`)
    result = reponse.data
  } catch (error: any) {
    console.log('Unable to retrieve the files info', error)
    storeApp.alertsWarning('Unable to retrieve the files info')
  }
  return result
}

async function uploadFiles(uploadFiles: FileList) {
  if (storeProjectId.projectId == null) {
    return
  }
  const uploadFileRequestsList = []
  for (const uploadFile of uploadFiles) {
    const newFile: File = {
      id: storeApp.constants.genFakeId,
      project_id: storeProjectId.projectId,
      filename: uploadFile.name,
      filesize: uploadFile.size,
      title: uploadFile.name,
      uploaded_on: new Date().toISOString(),
      hash: storeApp.constants.fakeHash,
      type: uploadFile.type,
      status: FileStatus.UPLOADING
    }
    files.value.set(newFile.id, { file: newFile, uploadedSize: 0 })

    const requestData = new FormData()
    requestData.append('project_id', storeProjectId.projectId)
    requestData.append('uploaded_file', uploadFile)

    const config = {
      onUploadProgress: (progressEvent: any) => {
        if (files.value.has(newFile.id)) {
          files.value.get(newFile.id)!.uploadedSize = progressEvent.loaded
        }
        console.log(progressEvent.loaded)
      }
    }

    uploadFileRequestsList.push(
      storeApp.axiosInstance
        .post<File>(`/projects/${storeProjectId.projectId}/files`, requestData, config)
        .then((response) => {
          if (files.value.has(newFile.id)) {
            files.value.get(newFile.id)!.file = response.data
          }
        })
        .catch((error) => {
          console.log(error)
          if (axios.isAxiosError(error)) {
            if (files.value.has(newFile.id)) {
              files.value.get(newFile.id)!.statusCode = error.code
              files.value.get(newFile.id)!.statusText = error.message
              files.value.get(newFile.id)!.file.status = FileStatus.FAILURE
            }
          }
        })
    )

    axios.all(uploadFileRequestsList)
  }
}

async function dropFilesHandler(fileList: FileList, uploadFileSize: number) {
  let totalSize = 0

  files.value.forEach((element) => {
    totalSize += element.file.filesize
  })

  if (totalSize + uploadFileSize > storeApp.constants.env.NAUTILUS_PROJECT_QUOTA) {
    storeApp.alertsWarning('Uploading file(s) exceed the quota')
    return
  }

  uploadFiles(fileList)
}

async function deleteFiles() {
  const deletedFiles: File[] = []

  for (const [key, file] of toBeDeletedFiles.value) {
    try {
      await storeApp.axiosInstance.delete(`/projects/${storeProjectId.projectId}/files/${file.id}`)
      if (selectedFiles.value.has(key)) {
        selectedFiles.value.delete(key)
      }
      files.value.delete(key)

      deletedFiles.push(file)
    } catch (error: any) {
      console.log('Unable to delete the file', storeProjectId.projectId, error)
      storeApp.alertsWarning(`Unable to delete the file: ${file.filename}`)
    }
  }

  if (deletedFiles.length == 1) {
    storeApp.alertsSuccess(`File ${deletedFiles[0].filename}has been removed`)
  } else {
    storeApp.alertsSuccess(`${deletedFiles.length} files have been removed`)
  }
}

async function deleteSingleFile(key: string, file: File) {
  toBeDeletedFiles.value.clear()
  toBeDeletedFiles.value.set(key, file)
  deletionModal.value?.showModal()
}

async function deleteSelectedFiles() {
  toBeDeletedFiles.value.clear()
  selectedFiles.value.forEach((_, key) => {
    const clientVisibleFile = files.value.get(key)
    if (clientVisibleFile?.file != undefined) {
      toBeDeletedFiles.value.set(key, clientVisibleFile.file)
    }
  })
  deletionModal.value?.showModal()
}

async function toggleSelectFile(key: string) {
  if (selectedFiles.value.has(key)) {
    selectedFiles.value.delete(key)
  } else {
    selectedFiles.value.set(key, true)
  }
}

function updateSelectFiles(newValue: Map<string, boolean>) {
  selectedFiles.value = newValue
}

function updateCompareFunction(newFunction: CompareFunctionType) {
  compareFunction.value = newFunction
}
</script>

<style scoped>
.drag-field {
  height: 5em;
}

.custom-btn-outline-primary {
  .btn-outline-primary {
    --bs-btn-color: var(--main-color);
    --bs-btn-border-color: var(--main-color);
    --bs-btn-hover-bg: var(--main-color);
    --bs-btn-hover-border-color: var(--main-color);
    --bs-btn-active-bg: var(--main-color);
    --bs-btn-active-border-color: var(--main-color);
    --bs-btn-disabled-color: var(--main-color);
    --bs-btn-disabled-border-color: var(--main-color);
  }
}

.drag-active {
  border-style: dashed !important;
  border-color: var(--main-color) !important;
}
</style>
