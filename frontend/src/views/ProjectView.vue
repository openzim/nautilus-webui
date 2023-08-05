<template>
  <ul>
    <li v-for="file in files" :key="file.id">
      {{ file.filename }}
    </li>
  </ul>
</template>
<script setup lang="ts">
import { UploadStatus, type File } from '@/constants'
import { useAppStore } from '@/stores/stores'
import axios from 'axios'
import { ref, type Ref } from 'vue'

const storeApp = useAppStore()
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
      uploadStatus: UploadStatus.Uploading
    }
    files.value.push(newFile)
    const fileId = newFile.id
    const requestData = new FormData()
    requestData.append('project_id', props.projectId)
    requestData.append('uploaded_file', uploadFile)
    uploadFileRequestsList.push(
      axios
        .post<File>(
          `${storeApp.constants.env.NAUTILUS_WEB_API}/projects/${props.projectId}/files`,
          requestData
        )
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
