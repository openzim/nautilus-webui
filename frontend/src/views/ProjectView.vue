<template>
  <div class="card m-5">
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
          {{
            humanifyFileSize(
              Array.from(files.values()).reduce((pre, element) => pre + element.file.filesize, 0)
            )
          }}
          /
          {{ humanifyFileSize(storeApp.constants.env.NAUTILUS_PROJECT_QUOTA) }}
        </div>
      </div>
      <UploadFilesComponent @drop-files-handler="dropFilesHandler" v-show="isShowed">
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
              <tr>
                <th scope="col">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    value=""
                    :indeterminate="selectedFiles.size != 0 && selectedFiles.size < files.size"
                    :checked="selectedFiles.size != 0 && selectedFiles.size == files.size"
                    @change.prevent="toggleSelectAllFiles"
                  />
                </th>
                <th scope="col">Name</th>
                <th scope="col">File Size</th>
                <th scope="col">File Type</th>
                <th scope="col">Uploaded On</th>
                <th scope="col">Status</th>
                <th scope="col">Metadata</th>
                <th scope="col">
                  <button
                    type="button"
                    class="btn"
                    :disabled="selectedFiles.size == 0"
                    @click.prevent="deleteSelectedFiles"
                  >
                    <font-awesome-icon :icon="['fas', 'trash']" />
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              <FileTabRowComponent
                v-for="[key, file] in files"
                :key="key"
                :render-key="key"
                :render-file="file"
                :is-selected="selectedFiles.has(key)"
                :show-edit-button="isEditMode"
                @toggle-select-file="toggleSelectFile"
                @delete-file="deleteFile"
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
import FileTabRowComponent from '@/components/FileTabRowComponent.vue'
import { FileStatus, type File, type RenderFile, humanifyFileSize } from '@/constants'
import { useAppStore, useProjectIdStore, useInitialFilesStore } from '@/stores/stores'
import { fromMime } from 'human-filetypes'
import axios from 'axios'
import { ref, watch, type Ref } from 'vue'

const isEditMode = ref(false)
const isShowed = ref(true)
const storeApp = useAppStore()
const storeProjectId = useProjectIdStore()
const storeInitialFileStore = useInitialFilesStore()
const files: Ref<Map<string, RenderFile>> = ref(new Map())
const selectedFiles: Ref<Map<string, boolean>> = ref(new Map())
const totalSize = ref(0)

watch(files, (newFiles) => {
  newFiles.forEach((element) => {
    totalSize.value += element.file.filesize
  })
})

if (storeInitialFileStore.initialFiles.length == 0) {
  const apiFiles = await getAllFiles(storeProjectId.projectId)
  apiFiles.forEach((item) => files.value.set(item.id, { file: item, uploadedSize: item.filesize }))
} else {
  await uploadFiles(storeInitialFileStore.initialFiles)
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
              files.value.get(newFile.id)!.statusCode = error.response?.status
              files.value.get(newFile.id)!.statusText = error.response?.statusText
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

async function deleteFile(key: string, file: File) {
  try {
    await storeApp.axiosInstance.delete(`/projects/${storeProjectId.projectId}/files/${file.id}`)
    if (selectedFiles.value.has(key)) {
      selectedFiles.value.delete(key)
    }
    files.value.delete(key)
  } catch (error: any) {
    console.log('Unable to delete the file', storeProjectId.projectId, error)
    storeApp.alertsWarning(`Unable to delete the file: ${file.filename}`)
  }
}

async function deleteSelectedFiles() {
  selectedFiles.value.forEach((_, key) => {
    const renderFile = files.value.get(key)
    if (renderFile?.file != undefined) {
      deleteFile(key, renderFile.file)
    }
  })
}

async function toggleSelectFile(key: string) {
  if (selectedFiles.value.has(key)) {
    selectedFiles.value.delete(key)
  } else {
    selectedFiles.value.set(key, true)
  }
}

async function toggleSelectAllFiles() {
  if (selectedFiles.value.size < files.value.size) {
    selectedFiles.value.clear()
    files.value.forEach((_, key) => {
      selectedFiles.value.set(key, true)
    })
  } else {
    selectedFiles.value.clear()
  }
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
</style>
