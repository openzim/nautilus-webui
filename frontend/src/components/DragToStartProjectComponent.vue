<template>
  <div>
    <DragToStartField @dropFilesHandler="dropFilesHandler" />
  </div>
</template>

<script setup lang="ts">
import DragToStartField from '@/components/DropToStartField.vue'
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
    const createUserRespone = await storeApp.axiosInstance.post<User>('/users')
    user = createUserRespone.data
  } catch (error: any) {
    console.log('Unable to create a new user.', error)
    storeApp.alertsError('Unable to create a new user.')
    return [user, project]
  }

  try {
    const createProjectResponse = await storeApp.axiosInstance.post<Project>(
      '/projects/',
      projectRequestData
    )
    project = createProjectResponse.data
  } catch (error: any) {
    console.log('Unable to create a new project.', error)
    storeApp.alertsError('Unable to create a new project.')
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
