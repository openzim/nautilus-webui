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
import { ref, type Ref } from 'vue'

const props = defineProps<{ initialFiles: FileList | undefined; projectId: string | null }>()
const files: Ref<File[]> = ref([])

if (props.initialFiles == undefined) {
  files.value = await getAllFiles(props.projectId)
} else {
  await uploadFiles(props.initialFiles)
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
      project_id: props.projectId,
      filename: uploadFile.name,
      filesize: uploadFile.size,
      title: uploadFile.name,
      uploaded_on: new Date().toISOString(),
      hash: Constants.fakeHash,
      type: uploadFile.type,
      uploadStatus: UploadStatus.Uploading
    }
    files.value.push(newFile)
    const fileId = newFile.id
    const requestData = new FormData()
    requestData.append('project_id', props.projectId)
    requestData.append('uploaded_file', uploadFile)
    uploadFileRequestsList.push(
      axios
        .post<File>(`${env.NAUTILUS_WEB_API}/projects/${props.projectId}/files`, requestData)
        .then((response) => {
          files.value.forEach((element, index) => {
            if (element.id == fileId) {
              files.value[index] = response.data
              files.value[index].uploadStatus = UploadStatus.Success
            }
          })
        })
        .catch((error) => {
          console.log(error)
          files.value.forEach((element, index) => {
            if (element.id == fileId) {
              files.value[index].uploadStatus = UploadStatus.Failure
            }
          })
        })
    )
    axios.all(uploadFileRequestsList)
  }
}
</script>
