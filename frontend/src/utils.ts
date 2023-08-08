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
  } catch (error: Error) {
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
  } catch (error: Error) {
    console.log('Unable to validate the user', error)
  }
  return result
}
