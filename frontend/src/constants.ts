import { v4 as uuid } from 'uuid'
import { partial } from 'filesize'

export interface ClientVisibleFile {
  file: NautilusFile
  uploadedSize: number
  statusCode?: string
  statusText?: string
}

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
export class NautilusFile implements File {
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

  public constructor(
    id: string,
    project_id: string,
    filename: string,
    filesize: number,
    title: string,
    authors: string[] | undefined,
    description: string | undefined,
    uploaded_on: string,
    hash: string,
    type: string,
    status: FileStatus
  ) {
    this.id = id
    this.project_id = project_id
    this.filename = filename
    this.filesize = filesize
    this.title = title
    this.authors = authors
    this.description = description
    this.uploaded_on = uploaded_on
    this.hash = hash
    this.type = type
    this.status = status
  }

  get isEditable(): boolean {
    return this.status != FileStatus.FAILURE && this.status != FileStatus.UPLOADING
  }
}

export enum FileStatus {
  UPLOADING = 'UPLOADING',
  LOCAL = 'LOCAL',
  S3 = 'S3',
  FAILURE = 'failure'
}

export interface Environ {
  NAUTILUS_WEB_API: string
  NAUTILUS_FILE_QUOTA: number
  NAUTILUS_PROJECT_QUOTA: number
}

export interface AlertMessage {
  type: AlertType
  message: string
}

export enum AlertType {
  ERROR = 'danger',
  WARNING = 'warning',
  SUCCESS = 'success',
  INFO = 'info'
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

export const EmptyConstants = new Constants({
  NAUTILUS_WEB_API: 'noapi',
  NAUTILUS_FILE_QUOTA: 100000000,
  NAUTILUS_PROJECT_QUOTA: 100000000
})

// We use jedec, rather than the default iec to make the file size display more readable.
// After using jedec, the file will display MB instead of MiB
export const humanifyFileSize = partial({ standard: 'jedec', output: 'string' })

export type CompareFunctionType = (
  a: [string, ClientVisibleFile],
  b: [string, ClientVisibleFile]
) => number

export type FileMetadataForm = {
  title: string
  description: string
  authors: string[]
  filename: string
}
export interface MetadataEditorFormType {
  description: string
  authors: string[]
  filename: string
}
