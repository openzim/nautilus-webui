<template>
  <div>
    <DragToStartField @dropFilesHandler="dropFilesHandler" />
  </div>
</template>

<script setup lang="ts">
import DragToStartField from '@/components/DragToStartField.vue'
import { type Project } from '@/constants'
import type { User } from '@/constants'
import { useAppStore, useProjectIdStore, useInitialFilesStore } from '@/stores/stores'
import { createNewProject } from '@/utils';

const storeProjectId = useProjectIdStore()
const storeApp = useAppStore()
const storeInitialFiles = useInitialFilesStore()

async function createUserAndProject(): Promise<[User | null, Project | null]> {
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

  project = await createNewProject("First Project")

  return [user, project]
}

async function dropFilesHandler(files: FileList) {
  storeInitialFiles.setInitialFiles(files)
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
