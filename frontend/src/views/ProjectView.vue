<template>
  <ul>
    <li v-for="file in files" :key="file.id">
      {{ file.filename }}
    </li>
  </ul>
</template>
<script setup lang="ts">
import { Constants, UploadStatus, type File } from '@/constants'
import axios from 'axios'
import { ref, watch, type Ref } from 'vue'

const props = defineProps<{ initialFiles: FileList | undefined; projectId: string | null }>()
const files: Ref<File[]> = ref([])
const pendingFiles = ref(props.initialFiles)

if (pendingFiles.value == undefined) {
  files.value = await getAllFiles(props.projectId)
}

async function getAllFiles(projectId: string | null) {
  var result: File[] = []
  if (projectId == null) {
    return result
  }
  const env = await Constants.env
  try {
    const reponse = await axios.get<File[]>(`${env.NAUTILUS_WEB_API}/projects/${projectId}/files`)
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
  const env = await Constants.env
  for (const uploadFile of uploadFiles) {
    const newFile: File = {
      id: Constants.fakeId,
      project_id: Constants.fakeId,
      filename: uploadFile.name,
      filesize: uploadFile.size,
      title: uploadFile.name,
      uploaded_on: new Date().toISOString(),
      hash: Constants.fakeHash,
      type: uploadFile.type,
      uploadStatus: UploadStatus.Uploading
    }
    const fileIndex = files.value.push(newFile) - 1
    const requestData = new FormData()
    requestData.append('project_id', props.projectId)
    requestData.append('uploaded_file', uploadFile)
    uploadFileRequestsList.push(
      axios
        .post(`${env.NAUTILUS_WEB_API}/projects/${props.projectId}/files`, requestData)
        .then(() => {
          files.value[fileIndex].uploadStatus = UploadStatus.Success
        })
        .catch((error) => {
          console.log(error)
          files.value[fileIndex].uploadStatus = UploadStatus.Failure
        })
    )
    axios.all(uploadFileRequestsList)
    pendingFiles.value = undefined
  }
}

watch(pendingFiles, async (newFiles) => {
  await uploadFiles(newFiles)
})

if (pendingFiles.value != undefined) {
  await uploadFiles(pendingFiles.value)
}
</script>
