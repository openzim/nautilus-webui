import { useAppStore } from './stores/stores'
import type { Project } from '@/constants'

/** Checks if a given project ID is valid */
export async function validProjectID(id: string | null) {
  if (id == null) {
    return false
  }
  const storeApp = useAppStore()
  let result = false
  try {
    await storeApp.axiosInstance.get<Project>(`/projects/${id}`)
    result = true
  } catch (error: unknown) {
    console.log('Unable to retrieve projectId', error, id)
  }
  return result
}

/** Checks if the User cookie is valid */
export async function validateUser() {
  const storeApp = useAppStore()
  let result = false
  try {
    await storeApp.axiosInstance.get<Project[]>('/projects')
    result = true
  } catch (error: unknown) {
    console.log('Unable to validate the user', error)
  }
  return result
}

export async function createNewProject(name: string): Promise<Project | null> {
  const storeApp = useAppStore()
  const projectRequestData = {
    name: name
  }
  try {
    const createProjectResponse = await storeApp.axiosInstance.post<Project>(
      '/projects',
      projectRequestData
    )
    return createProjectResponse.data
  } catch (error: any) {
    console.log('Unable to create a new project.', error)
    storeApp.alertsError('Unable to create a new project.')
    return null
  }
}
