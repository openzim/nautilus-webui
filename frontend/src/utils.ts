import { useAppStore, useProjectStore } from './stores/stores'
import type { Archive, Project } from '@/constants'
import router from '@/router'

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
    console.error('Unable to retrieve projectId', error, id)
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
    console.error('Unable to validate the user', error)
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
  } catch (error: unknown) {
    console.error('Unable to create a new project.', error)
    storeApp.alertsError('Unable to create a new project.')
    return null
  }
}

export async function updateProjects() {
  const storeProject = useProjectStore()
  const storeApp = useAppStore()
  try {
    const response = await storeApp.axiosInstance.get<Project[]>('/projects')
    storeProject.setProjects(response.data)
  } catch (error: unknown) {
    console.error('Unable to retrieve projects info', error)
    storeApp.alertsError('Unable to retrieve projects info')
    router.replace({ path: '/' })
  }
}

export async function refreshArchives() {
  const storeProject = useProjectStore()
  const storeApp = useAppStore()
  try {
    const response = await storeApp.axiosInstance.get<Archive[]>(
      `/projects/${storeProject.lastProjectId}/archives`
    )
    storeProject.setLastProjectArchives(response.data)
  } catch (error: unknown) {
    console.error('Unable to retrieve archives info', error)
    storeApp.alertsError('Unable to retrieve archives info')
  }
}

export async function set_project_webdav_path(webdav_path: string): Promise<string | null> {
  console.debug(`Setting WebDAV path to ${webdav_path}`)
  const storeProject = useProjectStore()
  const storeApp = useAppStore()
  const requestData = { webdav_path: webdav_path }
  let returned_path: string | null = null
  try {
    const response = await storeApp.axiosInstance.post<Project>(
      `/projects/${storeProject.lastProjectId}.dav`,
      requestData
    )
    if (response?.data?.webdav_path === undefined) return returned_path
    returned_path = response.data.webdav_path
    storeProject.replaceProject(response.data)
    storeApp.alertsSuccess(`Successfuly retrieved WebDAV info.`)
  } catch (error) {
    console.error(error)
    storeApp.alertsError(`Unable to get/set WebDAV info`)
  }
  return returned_path
}
