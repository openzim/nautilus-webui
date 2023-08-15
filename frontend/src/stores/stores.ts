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

  function alertsSuccess(message: string) {
    alertMessages.value.set(uuid(), { type: AlertType.SUCCESS, message: `SUCCESS: ${message}` })
  }

  function alertsInfo(message: string) {
    alertMessages.value.set(uuid(), { type: AlertType.INFO, message: `INFO: ${message}` })
  }

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
    } catch (error: unknown) {
      console.log('Unable to retrieve the environ.json file', error)
      alertsError('Unable to retrieve the environ.json file')
    }
  }

  return {
    alertsSuccess,
    alertsInfo,
    alertsError,
    alertsWarning,
    alertMessages,
    constants,
    axiosInstance,
    clearError,
    initConstants
  }
})

export const useInitialFilesStore = defineStore('initialFiles', () => {
  const initialFiles: Ref<FileList> = ref(new DataTransfer().files)

  function setInitialFiles(files: FileList) {
    initialFiles.value = files
  }
  return { initialFiles, setInitialFiles }
})
