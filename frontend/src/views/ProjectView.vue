<template>
  <ul>
    <li v-for="[key, file] in files" :key="key">
      {{ file.filename }}
    </li>
  </ul>
</template>
<script setup lang="ts">
import { FileStatus, type File } from '@/constants'
import { useAppStore } from '@/stores/stores'
import axios from 'axios'
import { ref, type Ref } from 'vue'

const storeApp = useAppStore()
const props = defineProps<{ initialFiles: FileList | undefined; projectId: string | null }>()
const files: Ref<Map<string, File>> = ref(new Map())

if (props.initialFiles == undefined) {
  const requestedFiles = await getAllFiles(props.projectId)
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
  }
  return result
}

async function uploadFiles(uploadFiles: FileList | undefined) {
  if (uploadFiles == undefined || props.projectId == null) {
    return
  }
  const uploadFileRequestsList = []
  for (const uploadFile of uploadFiles) {
    const newFile: File = {
      id: storeApp.constants.fakeId,
      project_id: props.projectId,
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
    requestData.append('project_id', props.projectId)
    requestData.append('uploaded_file', uploadFile)
    const config = {
      onUploadProgress: (progressEvent: any) => {
        //TODO: TRACK upload porgress.
        console.log(progressEvent.loaded)
      }
    }
    uploadFileRequestsList.push(
      axios
        .post<File>(
          `${storeApp.constants.env.NAUTILUS_WEB_API}/projects/${props.projectId}/files`,
          requestData,
          config
        )
        .catch((error) => {
          console.log(error)
          storeApp.alertsError(`Failed to upload: ${uploadFile.name}`)
        })
    )

    axios.all(uploadFileRequestsList)
  }
}
</script>
