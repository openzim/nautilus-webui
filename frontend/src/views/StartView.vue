<template>
  <div v-if="isVaildProjectID">
    <ProjectView :initial-files="storeInitialFileStore.initialFiles" />
  </div>
  <div v-else>
    <HomeView />
  </div>
</template>

<script setup lang="ts">
import ProjectView from '@/views/ProjectView.vue'
import HomeView from '@/views/HomeView.vue'
import { type Project } from '@/constants'
import axios from 'axios'
import { ref, watch } from 'vue'
import { useAppStore, useInitialFilesStore, useProjectIdStore } from '@/stores/stores'
import { validProjectID } from '@/utils'
import { validateUser } from '@/utils'
import { storeToRefs } from 'pinia'

const storeProjectId = useProjectIdStore()
const storeInitialFileStore = useInitialFilesStore()
const { projectId } = storeToRefs(storeProjectId)
const storeApp = useAppStore()
const isVaildProjectID = ref(await validProjectID(storeProjectId.projectId))

watch(projectId, async (newId) => {
  isVaildProjectID.value = await validProjectID(newId)
})

function clearCookies() {
  document.cookie.split(';').forEach(function (c) {
    document.cookie = c.trim().split('=')[0] + '=;max-age=0;'
  })
}

function getCookieByName(name: string): string | null {
  const nameLenPlus = name.length + 1
  return (
    document.cookie
      .split(';')
      .map((c) => c.trim())
      .filter((cookie) => {
        return cookie.substring(0, nameLenPlus) === `${name}=`
      })
      .map((cookie) => {
        return decodeURIComponent(cookie.substring(nameLenPlus))
      })[0] || null
  )
}

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
    if (axios.isAxiosError(error)) {
      storeApp.alertsError(`ERROR: ${error.response?.statusText}.`)
    }
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
