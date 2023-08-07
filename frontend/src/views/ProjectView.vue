<template>
  <ul>
    <li v-for="[key, file] in files" :key="key">
      {{ file.filename }}
    </li>
  </ul>
</template>
<script setup lang="ts">
import { FileStatus, type File } from '@/constants'
import { useAppStore, useProjectIdStore } from '@/stores/stores'
import axios from 'axios'
import { ref, type Ref } from 'vue'

const storeApp = useAppStore()
const storeProjectId = useProjectIdStore()
const props = defineProps<{ initialFiles: FileList | undefined }>()
const files: Ref<Map<string, File>> = ref(new Map())

if (props.initialFiles == undefined) {
  const requestedFiles = await getAllFiles(storeProjectId.projectId)
  requestedFiles.forEach((item) => files.value.set(item.id, item))
} else {
  await uploadFiles(props.initialFiles)
}

async function getAllFiles(projectId: string | null) {
  var result: File[] = []
  if (projectId == null) {
    return result
  }
  try {
    const reponse = await axios.get<File[]>(
      `${storeApp.constants.env.NAUTILUS_WEB_API}/projects/${projectId}/files`
    )
    result = reponse.data
  } catch (error: any) {
    console.log(error)
    storeApp.alertsError(error.message)
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
      status: FileStatus.LOCAL
    }
    files.value.set(newFile.id, newFile)

    const requestData = new FormData()
    requestData.append('project_id', storeProjectId.projectId)
    requestData.append('uploaded_file', uploadFile)
    const config = {
      onUploadProgress: (progressEvent: any) => {
        //TODO: track upload progress.
        console.log(progressEvent.loaded)
      }
    }
    uploadFileRequestsList.push(
      axios
        .post<File>(
          `${storeApp.constants.env.NAUTILUS_WEB_API}/projects/${storeProjectId.projectId}/files`,
          requestData,
          config
        )
        .catch((error) => {
          console.log(error)
          //TODO: Give users more personalized prompts based on different return codes.
          storeApp.alertsError(error.message)
        })
    )

    axios.all(uploadFileRequestsList)
  }
}
</script>
