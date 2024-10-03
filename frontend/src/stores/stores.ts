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
    const projects: Ref<Array<Project>> = ref([])
    const lastProject: Ref<Project | null> = ref(null)
    const lastProjectArchives: Ref<Array<Archive>> = ref([])
    const lastProjectPendingArchive: Ref<Archive | null> = ref(null)

    function setProjects(newIds: Array<Project>) {
      projects.value = newIds
      if (lastProjectId.value) {
        setLastProjectId(lastProjectId.value)
      }
    }

    function setLastProjectId(newId: string) {
      console.debug(
        `Switching to project: ${lastProject.value ? lastProject.value.id : null} -> #${newId}`
      )
      lastProjectId.value = newId
      lastProject.value =
        projects.value.filter((project) => project.id == lastProjectId.value).at(0) || null
    }

    function replaceProject(project: Project) {
      for (let idx: number = 0; idx <= projects.value.length; idx++) {
        if (projects.value[idx].id == project.id) {
          projects.value[idx].webdav_path = project.webdav_path
          return
        }
      }
      projects.value.push(project)
      setLastProjectId(project.id)
    }

    function clearLastProjectId() {
      lastProjectId.value = null
      lastProject.value = null
    }

    function setLastProjectArchives(archives: Archive[]) {
      lastProjectArchives.value = archives
      lastProjectPendingArchive.value =
        lastProjectArchives.value.filter((ark) => ark.status == 'PENDING').at(0) || null
    }

    function clearLastProjectArchives() {
      lastProjectArchives.value = []
      lastProjectPendingArchive.value = null
    }

    return {
      projects,
      lastProjectId,
      lastProject,
      lastProjectArchives,
      lastProjectPendingArchive,
      setLastProjectId,
      replaceProject,
      clearLastProjectId,
      setProjects,
      setLastProjectArchives,
      clearLastProjectArchives
    }
  },
  {
    persist: true
  }
)

export const useAppStore = defineStore('app', () => {
  const alertMessages: Ref<Map<string, AlertMessage>> = ref(new Map())
  const constants: Ref<Constants> = ref(EmptyConstants)
  const axiosInstance = ref(axios.create())
  let timeout: number = -1

  function alertsSuccess(message: string) {
    const mid = uuid()
    timeout = setTimeout(
      () => {
        clearTimeout(timeout)
        clearError(mid)
      },
      2000,
      mid
    )
    alertMessages.value.set(mid, { type: AlertType.SUCCESS, message: `SUCCESS: ${message}` })
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

    try {
      await axiosInstance.value
        .get(`/config`)
        .then((response) => {
          constants.value.env.NAUTILUS_STORAGE_URL = response.data.NAUTILUS_STORAGE_URL
        })
        .catch((error) => {
          console.error(`Unable to get STORAGE URL`, error)
        })
    } catch (error: unknown) {
      console.log('Error retrieving storage URL', error)
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
