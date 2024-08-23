import { useProjectStore } from '@/stores/stores'
import { ArchiveStatus, type Archive } from '@/constants'

export function getpreviousArchives(): Array<Archive> {
  const storeProject = useProjectStore()
  return storeProject.lastProjectArchives.filter((item) => item.status != ArchiveStatus.PENDING)
}

export function getLastPreviousArchive(): Archive {
  const previousArchives = getpreviousArchives()
  return previousArchives[previousArchives.length - 1]
}

export function getAdditionalPreviousArchives(): Array<Archive> {
  const previousArchives = getpreviousArchives()
  const lastPreviousArchive = getLastPreviousArchive()
  return previousArchives.filter((item) => item.id != lastPreviousArchive.id)
}

export function hasAdditionalPrevious(): boolean {
  return getAdditionalPreviousArchives().length > 0
}
