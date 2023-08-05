import axios from 'axios'
import { useAppStore } from './stores/stores'
import type { Project } from '@/constants'

export async function validProjectID(id: string | null) {
  const storeApp = useAppStore()
  let result = false
  if (id == null) {
    return result
  }
  try {
    await axios.get<Project>(`${storeApp.constants.env.NAUTILUS_WEB_API}/projects/${id}`)
    result = true
  } catch (error: any) {
    console.log(error)
    result = false
  }
  return result
}
