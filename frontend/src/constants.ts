import { v4 as uuid } from 'uuid'

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
  status: FileStatus
}

export enum FileStatus {
  UPLOADING = 'UPLOADING',
  LOCAL = 'LOCAL',
  S3 = 'S3'
}

export interface Environ {
  NAUTILUS_WEB_API: string
}

export interface AlertMessage {
  type: AlertType
  message: string
}

export enum AlertType {
  ERROR = 'danger',
  WARNING = 'warning'
}

export class Constants {
  env: Environ
  fakeHash: string

  constructor(env: Environ) {
    this.env = env
    this.fakeHash = ''
  }

  get genFakeId() {
    return uuid()
  }
}

export const EmptyConstants = new Constants({ NAUTILUS_WEB_API: 'noapi' })
