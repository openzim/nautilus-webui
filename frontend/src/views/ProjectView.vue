<template>
  <div class="card m-5" draggable="true">
    <div class="card-body">
      <h4 class="card-title">Card title</h4>
      <UploadFilesComponent @drop-files-handler="dropFilesHandler">
        <div>
          <table class="table">
            <thead>
              <tr>
                <th scope="col">
                  <input class="form-check-input" type="checkbox" value="" />
                </th>
                <th scope="col">Name</th>
                <th scope="col">File Size</th>
                <th scope="col">File Type</th>
                <th scope="col">Uploaded On</th>
                <th scope="col">Status</th>
                <th scope="col">Metadata</th>
                <th scope="col">
                  <button type="button" class="btn" disabled>
                    <font-awesome-icon :icon="['fas', 'trash']" />
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="[key, element] in files" :key="key">
                <th scope="row">
                  <input class="form-check-input" type="checkbox" value="" />
                </th>
                <td>{{ element.file.filename }}</td>
                <td>{{ element.file.filesize }}</td>
                <td>{{ element.file.type }}</td>
                <td>{{ element.file.uploaded_on }}</td>
                <td>
                  <div
                    class="progress"
                    role="progressbar"
                    v-if="element.file.status == FileStatus.UPLOADING"
                  >
                    <div
                      class="progress-bar"
                      :style="{ width: (element.uploadedSize / element.file.filesize) * 100 + '%' }"
                    />
                  </div>
                  <div v-else>
                    {{ element.file.status }}
                  </div>
                </td>
                <td>{{ element.file.authors + ' ' + element.file.description }}</td>
                <td>
                  <button type="button" class="btn" @click.prevent="deleteFile(element.file)">
                    <font-awesome-icon :icon="['fas', 'trash']" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="drag-field d-flex justify-content-center align-items-center">
            <h4>Drag Files to here</h4>
          </div>
        </div>
      </UploadFilesComponent>
    </div>
  </div>
</template>
<script setup lang="ts">
import { FileStatus, type File } from '@/constants'
import { useAppStore, useProjectIdStore, useInitialFilesStore } from '@/stores/stores'
import axios from 'axios'
import { ref, type Ref } from 'vue'
import UploadFilesComponent from '@/components/UploadFilesComponent.vue'

const storeApp = useAppStore()
const storeProjectId = useProjectIdStore()
const storeInitialFileStore = useInitialFilesStore()
const files: Ref<Map<string, RenderFile>> = ref(new Map())

interface RenderFile {
  file: File
  uploadedSize: number
  statusCode?: number
  statusText?: string
}

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

async function deleteFile(file: File) {
  try {
    await storeApp.axiosInstance.delete(`/projects/${storeProjectId.projectId}/files/${file.id}`)
    files.value.delete(file.id)
  } catch (error: any) {
    console.log('Unable to delete the file', storeProjectId.projectId, error)
    storeApp.alertsWarning(`Unable to delete the file: ${file.filename}`)
  }
}
</script>

<style>
.drag-field {
  height: 5em;
}
</style>
