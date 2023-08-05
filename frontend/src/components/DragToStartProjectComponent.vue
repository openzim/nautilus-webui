<template>
  <ProjectView :project-id="projectId" v-if="isValidProjectId" :initial-files="filesToUpload" />
  <DragToStartField v-else @dropFilesHandler="dropFilesHandler" />
</template>

<script setup lang="ts">
import DragToStartField from '@/components/DropToStartField.vue'
import ProjectView from '@/views/ProjectView.vue'
import axios from 'axios'
import { type Project } from '@/constants'
import { ref, watch, type Ref } from 'vue'
import type { User } from '@/constants'
import { useAppStore, useProjectIdStore } from '@/stores/stores'
import { validProjectID } from '@/utlis'

const storeProjectId = useProjectIdStore()
const storeApp = useAppStore()
const projectId: Ref<string | null> = ref(null)
const filesToUpload: Ref<FileList | undefined> = ref(undefined)
const isValidProjectId = ref(await validProjectID(projectId.value))

watch(projectId, async (newId) => {
  isValidProjectId.value = await validProjectID(newId)
})

async function createUserAndProject(): Promise<[Project, User]> {
  const user = await axios.post<User>(`${storeApp.constants.env.NAUTILUS_WEB_API}/users`)
  const projectRequestData = {
    name: 'First Project'
  }
  const createProjectResponse = await axios.post<Project>(
    `${storeApp.constants.env.NAUTILUS_WEB_API}/projects/`,
    projectRequestData
  )
  return [createProjectResponse.data, user.data]
}

async function dropFilesHandler(event: DragEvent) {
  filesToUpload.value = event.dataTransfer?.files
  setProjectAndUserIds(await createUserAndProject())
}

function setProjectAndUserIds(data: [Project, User]) {
  const [project] = data
  storeProjectId.setProjectId(project.id)
  projectId.value = project.id
}
</script>
