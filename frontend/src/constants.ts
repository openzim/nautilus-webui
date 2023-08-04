import axios from 'axios'

export interface Project {
  id: string
  name: string
  created_on: string
  expire_on?: string
}
export interface User {
  id: string
  created_on: string
}
interface Environ {
  NAUTILUS_WEBAPI: string
}
interface ConstantsInterface {
  env: Promise<Environ>
}

export const Constants: ConstantsInterface = {
  env: (async function () {
    try {
      const response = await axios.get<Environ>(`environ.json`)
      return response.data
    } catch (error) {
      return { NAUTILUS_WEBAPI: 'noapi' }
    }
  })()
}
