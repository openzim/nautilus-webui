<template>
  <ul>
    <li v-for="[key, file] in files" :key="key">
      {{ `${file.file.filename} ${file.uploadedSize} ${file.statusCode} ${file.statusText}` }}
    </li>
  </ul>
  <!--TODO: It's a place holder and need to be refactored -->
  <DragToStartField @dropFilesHandler="dropFilesHandler" />
</template>
<script setup lang="ts">
import DragToStartField from '@/components/DragToStartField.vue'
import { FileStatus, type File } from '@/constants'
import { useAppStore, useProjectIdStore, useInitialFilesStore } from '@/stores/stores'
import axios from 'axios'
import { ref, type Ref } from 'vue'

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

async function uploadFiles(uploadFiles: FileList | undefined) {
  if (uploadFiles == undefined || storeProjectId.projectId == null) {
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

async function dropFilesHandler(files: FileList) {
  uploadFiles(files)
}
</script>
