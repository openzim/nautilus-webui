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
import { validateUser } from '@/utlis'

const storeProjectId = useProjectIdStore()
const storeApp = useAppStore()
const projectId = ref(storeProjectId.projectId)
const isVaildProjectID = ref(await validProjectID(projectId.value))

watch(projectId, async (newId) => {
  isVaildProjectID.value = await validProjectID(newId)
})

function clearCookies() {
  document.cookie.split(';').forEach(function (c) {
    document.cookie =
      c.trim().split('=')[0] + '=;' + 'domain=*;path=/;expires=Thu, 01 Jan 1970 00:00:00 UTC;'
  })
}

async function setupProjectId() {
  try {
    const lastProject = (
      await axios.get<Project[]>(`${storeApp.constants.env.NAUTILUS_WEB_API}/projects`)
    ).data.pop()
    if (lastProject && (await validProjectID(lastProject?.id))) {
      projectId.value = lastProject.id
      storeProjectId.setProjectId(lastProject.id)
    }
  } catch (error: any) {
    console.log(error)
    storeApp.alertsError('Can not get project id.')
  }
}

if (!(await validateUser())) {
  storeApp.alertsError('Can not validate the user.')
  clearCookies()
} else if (!(await validProjectID(projectId.value))) {
  storeProjectId.clearProjectId()
  setupProjectId()
}
</script>
