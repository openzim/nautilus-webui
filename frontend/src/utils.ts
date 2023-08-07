import axios from 'axios'
import { useAppStore } from './stores/stores'
import type { Project } from '@/constants'

/** Checks if a given project ID is valid */
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

/** Clear all cookies */
export function clearCookies() {
  document.cookie.split(';').forEach(function (c) {
    document.cookie = c.trim().split('=')[0] + '=;max-age=0;'
  })
}

/** Get the value of a cookie value by its name */
export function getCookieByName(name: string): string | null {
  const nameLenPlus = name.length + 1
  return (
    document.cookie
      .split(';')
      .map((c) => c.trim())
      .filter((cookie) => {
        return cookie.substring(0, nameLenPlus) === `${name}=`
      })
      .map((cookie) => {
        return decodeURIComponent(cookie.substring(nameLenPlus))
      })[0] || null
  )
}
