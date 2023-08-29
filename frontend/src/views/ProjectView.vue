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
              <input
                type="radio"
                class="btn-check"
                name="btnradio"
                id="edit"
                autocomplete="off"
                @change="isEditMode = true"
                :checked="isEditMode"
              />
              <label class="btn btn-outline-primary" for="edit">Edit</label>

              <input
                type="radio"
                class="btn-check"
                name="btnradio"
                id="upload"
                autocomplete="off"
                @change="isEditMode = false"
                :checked="!isEditMode"
              />
              <label class="btn btn-outline-primary" for="upload">Upload</label>
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
                :editing-file-id="editingFileId"
                @update-editing-status="updateFileEditingStatus"
                @toggle-select-file="toggleSelectFile"
                @delete-file="deleteSingleFile"
                @update-file-metadata="updateFilesMetadata"
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
  FileClass,
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
const isEditMode = ref(false)
const editingFileId: Ref<string | null> = ref(null)
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
const toBeDeletedFiles: Ref<Map<string, FileClass>> = ref(new Map())
const compareFunction: Ref<CompareFunctionType> = ref((a, b) =>
  a[1].file.uploaded_on > b[1].file.uploaded_on ? 1 : -1
)
const sortedFiles: Ref<Map<string, ClientVisibleFile>> = computed(() =>
  sortFiles(files.value, compareFunction.value)
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
  var result: FileClass[] = []
  if (projectId == null) {
    return result
  }
  try {
    const reponse = await storeApp.axiosInstance.get<File[]>(`/projects/${projectId}/files`)
    for (const file of reponse.data) {
      result.push(
        new FileClass(
          file.id,
          file.project_id,
          file.filename,
          file.filesize,
          file.title,
          file.authors,
          file.description,
          file.uploaded_on,
          file.hash,
          file.type,
          file.status
        )
      )
    }
  } catch (error: any) {
    console.log('Unable to retrieve the files info', error)
    storeApp.alertsWarning('Unable to retrieve the files info')
  }
  return result
}

async function uploadFiles(uploadFiles: FileList) {
  if (storeProject.lastProjectId == null) {
    return
  }
  const uploadFileRequestsList = []
  for (const uploadFile of uploadFiles) {
    const newFile: FileClass = new FileClass(
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
            const data = response.data
            files.value.get(newFile.id)!.file = new FileClass(
              data.id,
              data.project_id,
              data.filename,
              data.filesize,
              data.title,
              data.authors,
              data.description,
              data.uploaded_on,
              data.hash,
              data.type,
              data.status
            )
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

    // After files are uploaded, check the project expiration date.
    axios.all(uploadFileRequestsList).finally(() => {
      updateProjects()
    })
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
  const deletedFiles: FileClass[] = []

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

async function deleteSingleFile(key: string, file: FileClass) {
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

async function updateFilesMetadata(
  renderId: string,
  fileId: string,
  newMetadata: FileMetadataForm
) {
  if (isEditMode.value == false) {
    updateSingleFileMetadata(renderId, fileId, newMetadata)
  } else {
    if (selectedFiles.value.size == 0) {
      for (const [id, file] of files.value.entries()) {
        if (file.file.isEditable) {
          updateSingleFileMetadata(id, file.file.id, newMetadata)
        }
      }
    } else {
      for (const renderId of selectedFiles.value.keys()) {
        const file = files.value.get(renderId)
        if (file != undefined && file.file.isEditable) {
          updateSingleFileMetadata(renderId, file.file.id, newMetadata)
        }
      }
    }
  }
}
async function updateSingleFileMetadata(
  clientFileId: string,
  fileId: string,
  newMetaData: FileMetadataForm
) {
  if (newMetaData.title == '') {
    storeApp.alertsWarning("Can not update file's metadata, since title is empty")
    return
  }
  if (newMetaData.filename == '') {
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
  files.value.get(clientFileId)!.file.title = newMetaData.title
  files.value.get(clientFileId)!.file.description = newMetaData.description
  files.value.get(clientFileId)!.file.authors = newMetaData.authors
  files.value.get(clientFileId)!.file.filename = newMetaData.filename
}
function updateFileEditingStatus(newId: string | null) {
  editingFileId.value = newId
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
