<template>
  <div>
    <DragToStartField @dropFilesHandler="dropFilesHandler" />
  </div>
</template>

<script setup lang="ts">
import DragToStartField from '@/components/DropToStartField.vue'
import axios from 'axios'
import { type Project } from '@/constants'
import type { User } from '@/constants'
import { useAppStore, useProjectIdStore, useInitialFilesStore } from '@/stores/stores'

const storeProjectId = useProjectIdStore()
const storeApp = useAppStore()
const storeInitialFiles = useInitialFilesStore()

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
  } catch (error: any) {
    console.log(error)
    storeApp.alertsError(error.message)
    return [user, project]
  }
  try {
    const createProjectResponse = await axios.post<Project>(
      `${storeApp.constants.env.NAUTILUS_WEB_API}/projects/`,
      projectRequestData
    )
    project = createProjectResponse.data
  } catch (error: any) {
    console.log(error)
    storeApp.alertsError(error.message)
  }
  return [user, project]
}

async function dropFilesHandler(event: DragEvent) {
  storeInitialFiles.setInitialFiles(event.dataTransfer?.files)
  const [, project] = await createUserAndProject()
  setProjectId(project)
}

function setProjectId(project: Project | null) {
  if (project == null) {
    return
  }
  storeProjectId.setProjectId(project.id)
}
</script>
