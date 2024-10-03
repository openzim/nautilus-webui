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
  webdav_path?: string
}

export interface Archive {
  id: string
  project_id: string
  status: string
  email?: string
  filesize?: number
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
  main_logo: string
  email: string
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
    return this.status == FileStatus.STORAGE
  }
}

export enum FileStatus {
  UPLOADING = 'UPLOADING',
  PROCESSING = 'PROCESSING',
  LOCAL = 'LOCAL',
  STORAGE = 'STORAGE',
  FAILURE = 'FAILURE'
}

export interface Environ {
  NAUTILUS_WEB_API: string
  NAUTILUS_FILE_QUOTA: number
  NAUTILUS_PROJECT_QUOTA: number
  NAUTILUS_FILE_REFRESH_EVERY_MS: number
  NAUTILUS_IS_SINGLE_USER: boolean
  NAUTILUS_STORAGE_URL: string
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
  NAUTILUS_FILE_REFRESH_EVERY_MS: 1000,
  NAUTILUS_IS_SINGLE_USER: false,
  NAUTILUS_STORAGE_URL: 'notset'
})

// using iec to be consistent accross tools (MiB): jedec renders MiB as MB
export const humanifyFileSize = partial({ standard: 'iec', output: 'string' })

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
  languages: string
  filename: string
  tags: string[]
  illustration: string
  main_logo: string
  email: string
}

export enum ArchiveStatus {
  PENDING = 'PENDING',
  REQUESTED = 'REQUESTED',
  READY = 'READY',
  FAILED = 'FAILED'
}

export const DEFAULT_MAIN_LOGO: string =
  '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'
export const DEFAULT_ILLUSTRATION: string =
  'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwAQMAAABtzGvEAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAANQTFRFR3BMgvrS0gAAAAF0Uk5TAEDm2GYAAAANSURBVBjTY2AYBdQEAAFQAAGn4toWAAAAAElFTkSuQmCC'
