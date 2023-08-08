import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { Constants, EmptyConstants, type AlertMessage, type Environ, AlertType } from '@/constants'
import { v4 as uuid } from 'uuid'
import axios from 'axios'

export const useProjectIdStore = defineStore(
  'projectId',
  () => {
    const projectId: Ref<string | null> = ref(null)

    function setProjectId(newId: string) {
      projectId.value = newId
    }

    function clearProjectId() {
      projectId.value = null
    }

    return { projectId, setProjectId, clearProjectId }
  },
  {
    persist: true
  }
)

export const useAppStore = defineStore('app', () => {
  const alertMessages: Ref<Map<string, AlertMessage>> = ref(new Map())
  const constants: Ref<Constants> = ref(EmptyConstants)
  const axiosInstance = ref(axios.create())

  function alertsError(message: string) {
    alertMessages.value.set(uuid(), { type: AlertType.ERROR, message: `ERROR: ${message}` })
  }

  function alertsWarning(message: string) {
    alertMessages.value.set(uuid(), { type: AlertType.WARNING, message: `WARNING: ${message}` })
  }

  function clearError(id: string) {
    alertMessages.value.delete(id)
  }

  async function initConstants() {
    try {
      const response = await axios.get<Environ>(`environ.json`)
      const env = response.data
      constants.value = new Constants(env)

      // Enable Cookies for Axios.
      axiosInstance.value = axios.create({ baseURL: env.NAUTILUS_WEB_API, withCredentials: true })
    } catch (error: Error) {
      console.log('Unable to retrieve the environ.json file', error)
      alertsError('Unable to retrieve the environ.json file')
    }
  }

  return {
    alertMessages,
    constants,
    axiosInstance,
    alertsError,
    alertsWarning,
    clearError,
    initConstants
  }
})

export const useInitialFilesStore = defineStore('initialFiles', () => {
  const initialFiles: Ref<FileList | undefined> = ref(undefined)

  function setInitialFiles(files: FileList | undefined) {
    initialFiles.value = files
  }
  return { initialFiles, setInitialFiles }
})
