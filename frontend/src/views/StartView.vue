<template>
  <div v-show="isVaildProjectID">
    <ProjectView :initial-files="undefined" />
  </div>
  <div v-show="!isVaildProjectID">
    <HomeView />
  </div>
</template>

<script setup lang="ts">
import ProjectView from '@/views/ProjectView.vue'
import HomeView from '@/views/HomeView.vue'
import { type Project } from '@/constants'
import axios from 'axios'
import { ref, watch } from 'vue'
import { useAppStore, useProjectIdStore } from '@/stores/stores'
import { validProjectID } from '@/utils'
import { validateUser } from '@/utils'
import { storeToRefs } from 'pinia'

const storeProjectId = useProjectIdStore()
const { projectId } = storeToRefs(storeProjectId)
const storeApp = useAppStore()
const isVaildProjectID = ref(await validProjectID(storeProjectId.projectId))

watch(projectId, async (newId) => {
  isVaildProjectID.value = await validProjectID(newId)
})

function clearCookies() {
  document.cookie.split(';').forEach(function (c) {
    document.cookie =
      c.trim().split('=')[0] + '=;' + 'domain=*;path=/;expires=Thu, 01 Jan 1970 00:00:00 UTC;'
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
    storeApp.alertsError('Can not get project id.')
  }
}

if (getCookieByName('user_id') != null) {
  if (!(await validateUser())) {
    storeApp.alertsError('Can not validate the user.')
    clearCookies()
    storeProjectId.clearProjectId()
  }
  if (!(await validProjectID(storeProjectId.projectId))) {
    setupProjectId()
  }
} else {
  storeProjectId.clearProjectId()
}
</script>
