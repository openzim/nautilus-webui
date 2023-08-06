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

async function createUserAndProject(): Promise<[User | null, Project | null]> {
  const projectRequestData = {
    name: 'First Project'
  }
  var user: User | null = null
  var project: Project | null = null
  try {
    const createUserRespone = await axios.post<User>(
      `${storeApp.constants.env.NAUTILUS_WEB_API}/users`
    )
    user = createUserRespone.data
  } catch (error) {
    console.log(error)
    storeApp.alertsError('Can not create the user.')
    return [user, project]
  }
  try {
    const createProjectResponse = await axios.post<Project>(
      `${storeApp.constants.env.NAUTILUS_WEB_API}/projects/`,
      projectRequestData
    )
    project = createProjectResponse.data
  } catch (error) {
    console.log(error)
    storeApp.alertsError('Can not create the user.')
    return [user, project]
  }
  return [user, project]
}

async function dropFilesHandler(event: DragEvent) {
  filesToUpload.value = event.dataTransfer?.files
  setProjectId(await createUserAndProject())
}

function setProjectId(data: [User | null, Project | null]) {
  const [, project] = data
  if (project == null) {
    return
  }
  storeProjectId.setProjectId(project.id)
  projectId.value = project.id
}
</script>
