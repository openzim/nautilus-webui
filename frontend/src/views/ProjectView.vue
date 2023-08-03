<template>
  <div v-if="hasErorr" class="alert alert-danger alert-dismissible" role="alert">
    <div>{{ errorMessage }}</div>
    <button type="button" @click="dismissAlert" class="btn-close" aria-label="Close"></button>
  </div>
  <DropToStartField @dropFilesHandler="dropFilesHandler" />
</template>

<script setup lang="ts">
import DropToStartField from '@/components/DropToStartField.vue'
import type { User, Project } from '@/constants'
import { Constants } from '@/constants'
import axios from 'axios'
import { ref } from 'vue'

const props = defineProps<{ project: Project | undefined }>()
const project = ref(props.project)
const hasErorr = ref(false)
const errorMessage = ref('')
function dismissAlert() {
  hasErorr.value = false
}

async function createUserAndProject() {
  const env = await Constants.env
  await axios.post<User>(`${env.NAUTILUS_WEBAPI}/users`)
  const projectRequestData = {
    name: 'First Project'
  }
  const createProjectResponse = await axios.post<Project>(
    `${env.NAUTILUS_WEBAPI}/projects`,
    projectRequestData
  )
  return createProjectResponse.data
}

async function dropFilesHandler(event: DragEvent) {
  if (event.dataTransfer?.files == undefined) {
    return
  }
  const files = event.dataTransfer.files
  const env = await Constants.env
  try {
    if (project.value == undefined) {
      project.value = await createUserAndProject()
    }
    const uploadFileRequestsList = []
    for (let i = 0; i < files.length; ++i) {
      const file = files[i]
      const requestData = new FormData()
      requestData.append('project_id', project.value.id)
      requestData.append('uploaded_file', file)
      uploadFileRequestsList.push(
        axios.post(`${env.NAUTILUS_WEBAPI}/projects/${project.value.id}/files`, requestData)
      )
    }
    await axios.all(uploadFileRequestsList)
  } catch (error: any) {
    hasErorr.value = true
    errorMessage.value = `${error.request.responseURL}: ${error.response.statusText}`
  }
}
</script>
