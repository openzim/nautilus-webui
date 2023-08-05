import { ref, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { Constants, EmptyConstants, type Environ } from '@/constants'
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
  const hasError = ref(false)
  const errorMessgae = ref('')
  const constants: Ref<Constants> = ref(EmptyConstants)

  function alertsError(messge: string) {
    hasError.value = true
    errorMessgae.value = messge
  }

  function clearError() {
    hasError.value = false
    errorMessgae.value = ''
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

  return { hasError, errorMessgae, constants, alertsError, clearError, initConstants }
})
