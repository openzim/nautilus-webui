<template>
  <div
    class="card m-5"
    :class="{ border: isActive, 'border-3': isActive, 'drag-active': isActive }"
  >
    <div class="card-body">
      <div
        class="card-title d-flex justify-content-between align-items-baseline"
        :class="{ 'border-bottom': isShowed }"
      >
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
      <UploadFilesComponent
        @drop-files-handler="dropFilesHandler"
        @update-is-active="updateIsActive"
        v-show="isShowed"
      >
        <div>
          <div class="d-flex flex-row-reverse">
            <div class="btn-group btn-group-sm custom-btn-outline-primary" role="group">
              <label class="btn btn-outline-primary" for="edit" :class="{ active: inEditMode }">
                <input
                  type="radio"
                  class="btn-check"
                  name="btnradio"
                  id="edit"
                  autocomplete="off"
                  @click.prevent="inEditMode = true"
                  :checked="inEditMode"
                />
                Edit
              </label>

              <label class="btn btn-outline-primary" for="upload" :class="{ active: !inEditMode }">
                <input
                  type="radio"
                  class="btn-check"
                  name="btnradio"
                  id="upload"
                  autocomplete="off"
                  @click.prevent="exitEditModeHandler"
                  :checked="!inEditMode"
                />
                Upload
              </label>
            </div>
          </div>
          <table class="table">
            <thead>
              <FileTableHeaderComponent
                :selected-files="selectedFiles"
                :files="files"
                @update-select-files="updateSelectFiles"
                @delete-selected-files="deleteSelectedFiles"
                @update-compare-function="updateCompareFunction"
              />
            </thead>
            <tbody>
              <FileTableRowComponent
                v-for="[renderId, file] in sortedFiles"
                :key="renderId"
                :render-id="renderId"
                :client-visible-file="file"
                :is-selected="selectedFiles.has(renderId)"
                :in-edit-mode="inEditMode"
                @toggle-select-file="toggleSelectFile"
                @delete-file="deleteSingleFile"
                @update-file-metadata-status="updateFileMetadataStatus"
                @update-single-file-metadata="updateSingleFileMetadata"
              />
            </tbody>
          </table>
          <div
            class="drag-field d-flex justify-content-center align-items-center"
            v-if="files.size <= 10"
          >
            <h4 style="color: var(--main-color); opacity: 0.6">Drag Files to here</h4>
          </div>
        </div>
      </UploadFilesComponent>
    </div>
  </div>
</template>
<script setup lang="ts">
import UploadFilesComponent from '@/components/UploadFilesComponent.vue'
import FileTableRowComponent from '@/components/FileTableRowComponent.vue'
import FileTableHeaderComponent from '@/components/FileTableHeaderComponent.vue'
import {
  FileStatus,
  type File,
  NautilusFile,
  type ClientVisibleFile,
  humanifyFileSize,
  type CompareFunctionType,
  type FileMetadataForm
} from '@/constants'
import { useAppStore, useProjectStore, useInitialFilesStore, useModalStore } from '@/stores/stores'
import axios from 'axios'
import { ref, type Ref, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { updateProjects } from '@/utils'

const isActive = ref(false)
const inEditMode = ref(false)
const isShowed = ref(true)
const storeApp = useAppStore()
const storeProject = useProjectStore()
const storeModal = useModalStore()
const { lastProjectId } = storeToRefs(storeProject)
const storeInitialFileStore = useInitialFilesStore()
const files: Ref<Map<string, ClientVisibleFile>> = ref(new Map())
const selectedFiles: Ref<Map<string, boolean>> = ref(new Map())
const totalSize = computed(() =>
  Array.from(files.value.values()).reduce((pre, element) => pre + element.file.filesize, 0)
)
const toBeDeletedFiles: Ref<Map<string, NautilusFile>> = ref(new Map())
const compareFunction: Ref<CompareFunctionType> = ref((a, b) =>
  a[1].file.uploaded_on > b[1].file.uploaded_on ? 1 : -1
)
const sortedFiles: Ref<Map<string, ClientVisibleFile>> = computed(() =>
  sortFiles(files.value, compareFunction.value)
)
const beUpdatedFile: Ref<Map<string, { fileId: string; metadata: FileMetadataForm }>> = ref(
  new Map()
)

watch(lastProjectId, async () => {
  await refreshFiles()
})

if (storeInitialFileStore.initialFiles.length == 0) {
  await refreshFiles()
} else {
  await uploadFiles(storeInitialFileStore.initialFiles)
}

async function refreshFiles() {
  files.value.clear()
  const apiFiles = await getAllFiles(storeProject.lastProjectId)
  apiFiles.forEach((item) => files.value.set(item.id, { file: item, uploadedSize: item.filesize }))
}

async function refreshFileStatus() {
  for (const [renderId, clientFile] of files.value.entries()) {
    if (clientFile.file.status != FileStatus.S3 && clientFile.file.status != FileStatus.FAILURE) {
      const newFile = await getSpecificFile(clientFile.file.project_id, clientFile.file.id)
      if (!newFile) {
        break
      }
      clientFile.file = NautilusFile.fromFile(newFile)
      if (files.value.has(renderId)) {
        files.value.set(renderId, clientFile)
      }
    }
  }
  setTimeout(async () => {
    await refreshFileStatus()
  }, storeApp.constants.env.NAUTILUS_REFRESH_TIME)
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
  var result: NautilusFile[] = []
  if (projectId == null) {
    return result
  }
  try {
    const response = await storeApp.axiosInstance.get<File[]>(`/projects/${projectId}/files`)
    for (const file of response.data) {
      result.push(NautilusFile.fromFile(file))
    }
  } catch (error: any) {
    console.log('Unable to retrieve the files info', error)
    storeApp.alertsWarning('Unable to retrieve the files info')
  }
  return result
}

async function getSpecificFile(projectId: string, fileId: string) {
  let result = null
  try {
    const response = await storeApp.axiosInstance.get<File>(
      `/projects/${projectId}/files/${fileId}`
    )
    result = response.data
  } catch (error: any) {
    console.log('Unable to retrieve the files info', error)
  }
  return result
}

async function uploadFiles(uploadFiles: FileList) {
  if (storeProject.lastProjectId == null) {
    return
  }
  const uploadFileRequestsList = []
  for (const uploadFile of uploadFiles) {
    const newFile: NautilusFile = new NautilusFile(
      storeApp.constants.genFakeId,
      storeProject.lastProjectId,
      uploadFile.name,
      uploadFile.size,
      uploadFile.name,
      undefined,
      undefined,
      new Date().toISOString(),
      storeApp.constants.fakeHash,
      uploadFile.type,
      FileStatus.UPLOADING
    )
    files.value.set(newFile.id, { file: newFile, uploadedSize: 0 })

    const requestData = new FormData()
    requestData.append('project_id', storeProject.lastProjectId)
    requestData.append('uploaded_file', uploadFile)

    const config = {
      onUploadProgress: (progressEvent: any) => {
        if (files.value.has(newFile.id)) {
          files.value.get(newFile.id)!.uploadedSize = progressEvent.loaded
        }
      }
    }

    uploadFileRequestsList.push(
      storeApp.axiosInstance
        .post<File>(`/projects/${storeProject.lastProjectId}/files`, requestData, config)
        .then((response) => {
          if (files.value.has(newFile.id)) {
            const uploadedFile = response.data
            files.value.get(newFile.id)!.file = NautilusFile.fromFile(uploadedFile)
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
  }

  // After files are uploaded, check the project expiration date.
  axios.all(uploadFileRequestsList).finally(() => {
    updateProjects()
  })
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
  const deletedFiles: NautilusFile[] = []

  for (const [key, file] of toBeDeletedFiles.value) {
    try {
      await storeApp.axiosInstance.delete(
        `/projects/${storeProject.lastProjectId}/files/${file.id}`
      )
      if (selectedFiles.value.has(key)) {
        selectedFiles.value.delete(key)
      }
      files.value.delete(key)

      deletedFiles.push(file)
    } catch (error: any) {
      console.log('Unable to delete the file', storeProject.lastProjectId, error)
      storeApp.alertsWarning(`Unable to delete the file: ${file.filename}`)
    }
  }

  if (deletedFiles.length == 1) {
    storeApp.alertsSuccess(`File ${deletedFiles[0].filename}has been removed`)
  } else {
    storeApp.alertsSuccess(`${deletedFiles.length} files have been removed`)
  }
}

async function deleteSingleFile(key: string, file: NautilusFile) {
  toBeDeletedFiles.value.clear()
  toBeDeletedFiles.value.set(key, file)
  storeModal.showModal(
    'Are you sure you want to delete:',
    'Delete',
    'Close',
    deleteFiles,
    async () => {
      toBeDeletedFiles.value.clear()
    },
    [file.title]
  )
}

async function deleteSelectedFiles() {
  toBeDeletedFiles.value.clear()
  selectedFiles.value.forEach((_, key) => {
    const clientVisibleFile = files.value.get(key)
    if (clientVisibleFile?.file != undefined) {
      toBeDeletedFiles.value.set(key, clientVisibleFile.file)
    }
  })
  let toBeDeletedFilesName = []
  for (let file of toBeDeletedFiles.value.values()) {
    toBeDeletedFilesName.push(file.title)
  }
  storeModal.showModal(
    'Are you sure you want to delete:',
    'Delete',
    'Close',
    deleteFiles,
    async () => {
      toBeDeletedFiles.value.clear()
    },
    toBeDeletedFilesName
  )
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

async function exitEditModeHandler() {
  if (!inEditMode.value) {
    return
  }
  const changeList = []

  for (const [key, element] of beUpdatedFile.value.entries()) {
    if (files.value.get(key) != undefined) {
      changeList.push(element.metadata.title)
    }
  }

  if (changeList.length == 0) {
    inEditMode.value = false
  } else {
    storeModal.showModal(
      'Are you sure you want to change those files:',
      'Change',
      'Discard',
      updateBeUpdatedFilesMetadata,
      async () => {
        inEditMode.value = false
      },
      changeList
    )
  }
}

async function updateBeUpdatedFilesMetadata() {
  for (const [key, element] of beUpdatedFile.value.entries()) {
    if (files.value.get(key) != undefined) {
      await updateSingleFileMetadata(key, element.fileId, element.metadata)
    }
  }
  inEditMode.value = false
  beUpdatedFile.value.clear()
}

async function updateFileMetadataStatus(
  renderId: string,
  fileId: string,
  newMetaData: FileMetadataForm
) {
  beUpdatedFile.value.set(renderId, { fileId: fileId, metadata: newMetaData })
}

async function updateSingleFileMetadata(
  renderId: string,
  fileId: string,
  newMetaData: FileMetadataForm
) {
  if (newMetaData.title.trim().length == 0) {
    storeApp.alertsWarning("Can not update file's metadata, since title is empty")
    return
  }
  if (newMetaData.filename.trim().length == 0) {
    storeApp.alertsWarning("Can not update file's metadata, since filename is empty")
    return
  }
  try {
    await storeApp.axiosInstance.patch<string>(
      `/projects/${lastProjectId.value}/files/${fileId}`,
      newMetaData
    )
  } catch (error) {
    console.log("Unable to update file's metadata.", error, fileId)
    storeApp.alertsError(`Unable to update file's metadata, file id: ${fileId}`)
  }
  files.value.get(renderId)!.file.title = newMetaData.title
  files.value.get(renderId)!.file.description = newMetaData.description
  files.value.get(renderId)!.file.authors = newMetaData.authors
  files.value.get(renderId)!.file.filename = newMetaData.filename
}

refreshFileStatus()
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
