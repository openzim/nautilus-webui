<template>
  <div class="mt-5">
    <SloganComponent />
    <div class="mt-5">
      <DropToStartField @dropFilesHandler="dropFilesHandler" />
    </div>
    <div class="mt-5">
      <FrequentlyAskedQuestions />
    </div>
  </div>
  <div v-if="hasErorr" class="alert alert-danger alert-dismissible" role="alert">
    <div>{{ errorMessage }}</div>
    <button type="button" @click="dismissAlert" class="btn-close" aria-label="Close"></button>
  </div>
</template>

<script setup lang="ts">
import SloganComponent from '@/components/SloganComponent.vue'
import DropToStartField from '@/components/DropToStartField.vue'
import FrequentlyAskedQuestions from '@/components/FrequentlyAskedQuestions.vue'
import { ref } from 'vue'
import axios from 'axios'
import router from '@/router'

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
  axios
    .post(`${import.meta.env.VITE_API_URL}/users`)
    .then(() => {
      const data = {
        name: 'First Project'
      }
      return axios.post(`${import.meta.env.VITE_API_URL}/projects`, data)
    })
    .then((response) => {
      const project_id = response.data.id
      const uploadFileRequestsList = []
      for (let i = 0; i < files.length; ++i) {
        const file = files[i]
        const requestData = new FormData()
        requestData.append('project_id', project_id)
        requestData.append('uploaded_file', file)
        uploadFileRequestsList.push(
          axios.post(`${import.meta.env.VITE_API_URL}/projects/${project_id}/files`, requestData)
        )
      }
      return axios.all(uploadFileRequestsList)
    })
    .then(() => {
      router.push({ path: '/project' })
    })
    .catch((error) => {
      hasErorr.value = true
      errorMessage.value = `${error.request.responseURL}: ${error.response.statusText}`
    })
}
</script>
