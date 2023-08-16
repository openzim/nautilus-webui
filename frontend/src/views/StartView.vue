<template>
  <div class="d-flex flex-column vh-100">
    <div class="flex-shrink-1">
      <Suspense>
        <ProjectView v-if="isVaildProjectID" />
        <HomeView v-else />
      </Suspense>
    </div>
    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import FooterComponent from '@/components/FooterComponent.vue'
import ProjectView from '@/views/ProjectView.vue'
import HomeView from '@/views/HomeView.vue'
import { type Project } from '@/constants'
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

async function setupProjectId() {
  try {
    const lastProject = (await storeApp.axiosInstance.get<Project[]>('/projects')).data.pop()
    if (lastProject && (await validProjectID(lastProject?.id))) {
      storeProjectId.setProjectId(lastProject.id)
    }
  } catch (error: any) {
    console.log('Unable to retrieve the last project id', error)
    storeApp.alertsWarning('Unable to the retrieve last project id.')
    storeProjectId.clearProjectId()
  }
}

if (
  (storeProjectId.projectId != undefined && !(await validProjectID(storeProjectId.projectId))) ||
  (await validateUser())
) {
  setupProjectId()
}
</script>
