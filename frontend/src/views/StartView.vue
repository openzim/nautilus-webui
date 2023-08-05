<template>
  <ProjectView :project-id="projectId" :initial-files="undefined" v-if="isVaildProjectID" />
  <HomeView v-else />
</template>

<script setup lang="ts">
import ProjectView from '@/views/ProjectView.vue'
import HomeView from '@/views/HomeView.vue'
import { type Project } from '@/constants'
import axios from 'axios'
import { ref, watch } from 'vue'
import { useAppStore, useProjectIdStore } from '@/stores/stores'
import { validProjectID } from '@/utlis'

const storeProjectId = useProjectIdStore()
const storeApp = useAppStore()
const projectId = ref(storeProjectId.projectId)
const isVaildProjectID = ref(await validProjectID(projectId.value))

watch(projectId, async () => {
  isVaildProjectID.value = await validProjectID(projectId.value)
})

async function setupProjectId() {
  try {
    const lastProject = (
      await axios.get<Project[]>(`${storeApp.constants.env.NAUTILUS_WEB_API}/projects`)
    ).data.pop()
    if (lastProject && (await validProjectID(lastProject?.id))) {
      projectId.value = lastProject.id
    }
  } catch (error: any) {
    storeApp.alertsError('Can not setup project id.')
    console.log(error)
  }
}
if (projectId.value && !validProjectID(projectId.value)) {
  setupProjectId()
}
</script>
