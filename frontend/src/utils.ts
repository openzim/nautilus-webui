import axios from 'axios'
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
    await axios.get<Project>(`${storeApp.constants.env.NAUTILUS_WEB_API}/projects/${id}`)
    result = true
  } catch (error: any) {
    console.log(error)
    storeApp.alertsError(error.message)
    if (axios.isAxiosError(error) && error.response?.status == 404) {
      result = false
    }
  }
  return result
}

/** Checks if the User cookie is valid */
export async function validateUser() {
  const storeApp = useAppStore()
  let result = true
  try {
    await axios.get<Project[]>(`${storeApp.constants.env.NAUTILUS_WEB_API}/projects`)
    result = true
  } catch (error: any) {
    console.log(error)
    storeApp.alertsError(error.message)
    if (axios.isAxiosError(error) && error.response?.status == 401) {
      result = false
    }
  }
  return result
}
