<template>
  <div class="d-flex flex-column vh-100">
    <div class="flex-shrink-1">
      <p>Retrieving single user & projects…</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { type Project } from '@/constants'
import type { User } from '@/constants'
import { useAppStore, useProjectStore } from '@/stores/stores'
import { createNewProject } from '@/utils'
import router from '@/router'

const storeProject = useProjectStore()
const storeApp = useAppStore()

async function restrieveUser(): Promise<User | null> {
  var user: User | null = null

  try {
    const createUserRespone = await storeApp.axiosInstance.post<User>('/users')
    user = createUserRespone.data
  } catch (error: any) {
    console.log('Unable to create a new user.', error)
    storeApp.alertsError('Unable to create a new user.')
  }
  return user
}

async function retrieveProjects(): Promise<Project[]> {
  var projects: Project[] = []
  try {
    const response = await storeApp.axiosInstance.get<Project[]>('/projects')
    console.log(response.data)
    projects = response.data
  } catch (error: unknown) {
    console.log('Unable to retrieve projects info', error)
    storeApp.alertsError('Unable to retrieve projects info')
  }

  if (projects.length == 0) {
    let project: Project | null = await createNewProject('First Project')
    if (project !== null) {
      projects.push(project)
    }
  }

  return projects
}

await restrieveUser()
const projects = await retrieveProjects()
storeProject.setProjects(projects)
if (projects.length) {
  storeProject.setLastProjectId(projects[projects.length - 1].id)
}
router.push('/collections')
</script>
