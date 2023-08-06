import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { Constants, EmptyConstants, type Environ } from '@/constants'
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
  const errorMessgae: Ref<Map<string, string>> = ref(new Map())
  const constants: Ref<Constants> = ref(EmptyConstants)

  function alertsError(message: string) {
    errorMessgae.value.set(uuid(), message)
  }

  function clearError(id: string) {
    errorMessgae.value.delete(id)
  }

  async function initConstants() {
    try {
      const response = await axios.get<Environ>(`environ.json`)
      const env = response.data
      constants.value = new Constants(env)
    } catch (error: any) {
      alertsError('Can not get environ.json file')
    }
  }

  return { errorMessgae, constants, alertsError, clearError, initConstants }
})

export const useInitialFilesStore = defineStore('initialFiles', () => {
  const initialFiles: Ref<FileList | undefined> = ref(undefined)

  function setInitialFiles(files: FileList | undefined) {
    initialFiles.value = files
  }
  return { initialFiles, setInitialFiles }
})
