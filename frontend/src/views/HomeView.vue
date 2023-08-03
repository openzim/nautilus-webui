<template>
  <div class="mt-5">
    <SloganComponent />
    <div class="mt-5">
      <div v-if="hasErorr" class="alert alert-danger alert-dismissible" role="alert">
        <div>{{ errorMessage }}</div>
        <button type="button" @click="dismissAlert" class="btn-close" aria-label="Close"></button>
      </div>
      <DropToStartField @dropFilesHandler="dropFilesHandler" />
    </div>
    <div class="mt-5">
      <FrequentlyAskedQuestions />
    </div>
  </div>
</template>

<script setup lang="ts">
import SloganComponent from '@/components/SloganComponent.vue'
import DropToStartField from '@/components/DropToStartField.vue'
import FrequentlyAskedQuestions from '@/components/FrequentlyAskedQuestions.vue'
import { ref } from 'vue'
import axios from 'axios'
import { Constants, type Project, type User } from '@/constants'

const hasErorr = ref(false)
const errorMessage = ref('')

function dismissAlert() {
  hasErorr.value = false
}

async function dropFilesHandler(event: DragEvent) {
  if (event.dataTransfer?.files == undefined) {
    return
  }
  const files = event.dataTransfer.files
  const env = await Constants.env
  try {
    await axios.post<User>(`${env.NAUTILUS_WEBAPI}/users`)
    const projectRequestData = {
      name: 'First Project'
    }
    const createProjectResponse = await axios.post<Project>(
      `${env.NAUTILUS_WEBAPI}/projects`,
      projectRequestData
    )
    const uploadFileRequestsList = []
    for (let i = 0; i < files.length; ++i) {
      const file = files[i]
      const requestData = new FormData()
      requestData.append('project_id', createProjectResponse.data.id)
      requestData.append('uploaded_file', file)
      uploadFileRequestsList.push(
        axios.post(
          `${env.NAUTILUS_WEBAPI}/projects/${createProjectResponse.data.id}/files`,
          requestData
        )
      )
    }
    await axios.all(uploadFileRequestsList)
  } catch (error: any) {
    hasErorr.value = true
    errorMessage.value = `${error.request.responseURL}: ${error.response.statusText}`
  }
}
</script>
