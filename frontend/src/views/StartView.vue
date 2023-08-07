<template>
  <ProjectView v-if="isVaildProjectID" />
  <HomeView v-else />
</template>

<script setup lang="ts">
import ProjectView from '@/views/ProjectView.vue'
import HomeView from '@/views/HomeView.vue'
import { type Project } from '@/constants'
import axios from 'axios'
import { ref, watch } from 'vue'
import { useAppStore, useProjectIdStore } from '@/stores/stores'
import { clearCookies, getCookieByName, validProjectID } from '@/utils'
import { validateUser } from '@/utils'
import { storeToRefs } from 'pinia'

const storeProjectId = useProjectIdStore()
const { projectId } = storeToRefs(storeProjectId)
const storeApp = useAppStore()
const isVaildProjectID = ref(await validProjectID(storeProjectId.projectId))

watch(projectId, async (newId) => {
  isVaildProjectID.value = await validProjectID(newId)
})

async function setupProjectId() {
  try {
    const lastProject = (
      await axios.get<Project[]>(`${storeApp.constants.env.NAUTILUS_WEB_API}/projects`)
    ).data.pop()
    if (lastProject && (await validProjectID(lastProject?.id))) {
      storeProjectId.setProjectId(lastProject.id)
    }
  } catch (error: any) {
    console.log(error)
    storeApp.alertsError(error.message)
  }
}

if (getCookieByName('user_id') != null) {
  if (!(await validateUser())) {
    storeApp.alertsError('Can not validate the user.')
    clearCookies()
    storeProjectId.clearProjectId()
  } else if (!(await validProjectID(storeProjectId.projectId))) {
    setupProjectId()
  }
} else {
  storeProjectId.clearProjectId()
}
</script>
