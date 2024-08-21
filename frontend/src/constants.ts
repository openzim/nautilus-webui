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

export interface Archive {
  id: string
  project_id: string
  status: string
  email?: string
  filesize?: int
  created_on: string
  requested_on?: string
  completed_on?: string
  download_url?: string
  config: ArchiveConfig
}

export interface ArchiveConfig {
  title: string
  description: string
  name: string
  publisher: string
  creator: string
  languages: string
  tags: string[]
  illustration: string
  filename: string
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

  public static fromFile(file: File): NautilusFile {
    return new NautilusFile(
      file.id,
      file.project_id,
      file.filename,
      file.filesize,
      file.title,
      file.authors,
      file.description,
      file.uploaded_on,
      file.hash,
      file.type,
      file.status
    )
  }

  get isEditable(): boolean {
    return this.status == FileStatus.S3
  }
}

export enum FileStatus {
  UPLOADING = 'UPLOADING',
  PROCESSING = 'PROCESSING',
  LOCAL = 'LOCAL',
  S3 = 'S3',
  FAILURE = 'FAILURE'
}

export interface Environ {
  NAUTILUS_WEB_API: string
  NAUTILUS_FILE_QUOTA: number
  NAUTILUS_PROJECT_QUOTA: number
  NAUTILUS_FILE_REFRESH_EVERY_MS: number
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
  NAUTILUS_PROJECT_QUOTA: 100000000,
  NAUTILUS_FILE_REFRESH_EVERY_MS: 1000
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


export type ArchiveMetadataFormType = {
  title: string
  description: string
  name: string
  creator: string
  publisher: string
  language: string
  filename: string
  tags: string[]
}


export enum ArchiveStatus {
  PENDING = 'PENDING',
  REQUESTED = 'REQUESTED',
  READY = 'READY',
  FAILED = 'FAILED',

}
