import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import {
  Constants,
  EmptyConstants,
  type AlertMessage,
  type Environ,
  AlertType,
  type Project,
  type Archive
} from '@/constants'
import { v4 as uuid } from 'uuid'
import axios from 'axios'

export const useProjectStore = defineStore(
  'projectId',
  () => {
    const lastProjectId: Ref<string | null> = ref(null)
    const projects: Ref<Project[]> = ref([])
    const lastProject: Ref<Project | null> = ref(null)
    const lastProjectArchives: Ref<Archive[]> = ref([])
    const lastProjectPendingArchive: Ref<Archive | null> = ref(null)

    function setProjects(newIds: Project[]) {
      projects.value = newIds
      if (lastProjectId.value) {
        lastProject.value = projects.value.filter((project) => project.id == lastProjectId.value).at(0) || null
      }
    }

    function setLastProjectId(newId: string) {
      lastProjectId.value = newId
      lastProject.value = projects.value.filter((project) => project.id == lastProjectId.value).at(0) || null
    }

    function clearLastProjectId() {
      lastProjectId.value = null
      lastProject.value = null
    }

    function setLastProjectArchives(archives: Archive[]) {
      lastProjectArchives.value = archives
      lastProjectPendingArchive.value = lastProjectArchives.value.filter((ark) => ark.status == "PENDING").at(0) || null
    }

    function clearLastProjectArchives() {
      lastProjectArchives.value = []
      lastProjectPendingArchive.value = null
    }

    return { projects, lastProjectId, lastProject, lastProjectArchives, lastProjectPendingArchive, setLastProjectId, clearLastProjectId, setProjects, setLastProjectArchives, clearLastProjectArchives }
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

export const useModalStore = defineStore('modal', () => {
  const isShown = ref(false)
  const title = ref('')
  const primaryButtonTitle = ref('')
  const secondaryButtonTitle = ref('')
  const clickPrimaryButton = ref(async () => {})
  const clickSecondaryButton = ref(async () => {})
  const content: Ref<string[]> = ref([])

  function showModal(
    newTitle: string,
    newPrimaryButtonTitle: string,
    newSecondaryButtonTitle: string,
    newClickPrimaryButton: () => Promise<void>,
    newClickSecondaryButton: () => Promise<void>,
    newContent: string[]
  ) {
    title.value = newTitle
    primaryButtonTitle.value = newPrimaryButtonTitle
    secondaryButtonTitle.value = newSecondaryButtonTitle
    clickPrimaryButton.value = newClickPrimaryButton
    clickSecondaryButton.value = newClickSecondaryButton
    content.value = newContent
    isShown.value = true
  }

  function dismissModal() {
    isShown.value = false
  }
  return {
    title,
    primaryButtonTitle,
    secondaryButtonTitle,
    clickPrimaryButton,
    clickSecondaryButton,
    content,
    isShown,
    showModal,
    dismissModal
  }
})
