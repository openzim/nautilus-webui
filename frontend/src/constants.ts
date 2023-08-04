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

export interface File {
  id: string
  project_id: string
  filename: string
  filesize: number
  title: string
  authors?: string[]
  description?: string
  uploaded_on: string
  hash: string
  type: string
  uploadStatus: UploadStatus
}

export enum UploadStatus {
  Uploading = 'Uploading',
  Success = 'Success',
  Failure = 'Failure'
}

interface Environ {
  NAUTILUS_WEBAPI: string
}
interface ConstantsInterface {
  env: Promise<Environ>
  fakeId: string
  fakeHash: string
}

export const Constants: ConstantsInterface = {
  env: (async function () {
    try {
      const response = await axios.get<Environ>(`environ.json`)
      return response.data
    } catch (error) {
      return { NAUTILUS_WEBAPI: 'noapi' }
    }
  })(),
  fakeId: 'ffffffff-ffff-ffff-ffff-ffffffffffff',
  fakeHash: 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
}

export async function validProjectID(id: string | null) {
  if (id == null) {
    return false
  }
  const env = await Constants.env
  try {
    await axios.get<Project>(`${env.NAUTILUS_WEBAPI}/projects/${id}`)
    return true
  } catch (error: any) {
    console.log(error)
    return false
  }
}
