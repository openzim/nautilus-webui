<template>
  <ProjectView :project-id="projectId" :initial-files="undefined" v-if="isVaildProjectID" />
  <HomeView v-else />
</template>

<script setup lang="ts">
import ProjectView from '@/views/ProjectView.vue'
import HomeView from '@/views/HomeView.vue'
import { Constants, validProjectID, type Project } from '@/constants'
import axios from 'axios'
import { ref, watch } from 'vue'

const projectId = ref(localStorage.getItem('projectId'))
const isVaildProjectID = ref(await validProjectID(projectId.value))

watch(projectId, async () => {
  isVaildProjectID.value = await validProjectID(projectId.value)
})

async function setupProjectId() {
  const env = await Constants.env
  try {
    const lastProject = (await axios.get<Project[]>(`${env.NAUTILUS_WEB_API}/projects`)).data.pop()
    if (lastProject && (await validProjectID(lastProject?.id))) {
      projectId.value = lastProject.id
    }
  } catch (error: any) {
    console.log(error)
  }
}
if (projectId.value && !validProjectID(projectId.value)) {
  setupProjectId()
}
</script>
