<template>
  <ProjectView :project-id="projectId" v-if="isValidProjectId" :initial-files="filesToUpload" />
  <DragToStartField v-else @dropFilesHandler="dropFilesHandler" />
</template>

<script setup lang="ts">
import DragToStartField from '@/components/DropToStartField.vue'
import ProjectView from '@/views/ProjectView.vue'
import axios from 'axios'
import { validProjectID, type Project } from '@/constants'
import { Constants } from '@/constants'
import { ref, watch, type Ref } from 'vue'
import type { User } from '@/constants'
import { useProjectIdStore } from '@/stores/counter'

const storeProjectId = useProjectIdStore()
const projectId: Ref<string | null> = ref(null)
const filesToUpload: Ref<FileList | undefined> = ref(undefined)
const isValidProjectId = ref(await validProjectID(projectId.value))

watch(projectId, async (newId) => {
  isValidProjectId.value = await validProjectID(newId)
})

async function createUserAndProject(): Promise<[Project, User]> {
  const env = await Constants.env
  const user = await axios.post<User>(`${env.NAUTILUS_WEB_API}/users`)
  const projectRequestData = {
    name: 'First Project'
  }
  const createProjectResponse = await axios.post<Project>(
    `${env.NAUTILUS_WEB_API}/projects/`,
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
