<template>
  <div class="d-flex flex-column vh-100">
    <div class="flex-shrink-1">
      <Suspense>
        <CollectionsView v-if="isValidProjectId" />
        <HomeView v-else />
      </Suspense>
    </div>
    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import FooterComponent from '@/components/FooterComponent.vue'
import CollectionsView from './CollectionsView.vue'
import HomeView from '@/views/HomeView.vue'
import { type Project } from '@/constants'
import { ref, watch } from 'vue'
import { useAppStore, useProjectStore } from '@/stores/stores'
import { validProjectID } from '@/utils'
import { validateUser } from '@/utils'
import { storeToRefs } from 'pinia'
import router from '@/router'

const storeProject = useProjectStore()
const { lastProjectId } = storeToRefs(storeProject)
const storeApp = useAppStore()
const isValidProjectId = ref(await validProjectID(storeProject.lastProjectId))

watch(lastProjectId, async (newId) => {
  isValidProjectId.value = await validProjectID(newId)
})

async function setupProjectId() {
  try {
    const lastProject = (await storeApp.axiosInstance.get<Project[]>('/projects')).data.pop()
    if (lastProject && (await validProjectID(lastProject?.id))) {
      storeProject.setLastProjectId(lastProject.id)
    }
  } catch (error: any) {
    console.log('Unable to retrieve the last project id', error)
    storeApp.alertsWarning('Unable to the retrieve last project id.')
    storeProject.clearLastProjectId()
  }
}

if (
  (storeProject.lastProjectId != undefined &&
    !(await validProjectID(storeProject.lastProjectId))) ||
  (await validateUser())
) {
  setupProjectId()
  if (await validateUser()) {
    router.push('/collections')
  }
}
</script>
