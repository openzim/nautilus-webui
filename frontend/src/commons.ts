import { ref, type computed } from 'vue'
import { useProjectStore } from '@/stores/stores'
import { ArchiveStatus } from '@/constants'


// const previousArchives: Array<Archive> = computed(() => storeProject.lastProjectArchives.filter((item) => item.status != ArchiveStatus.PENDING))
// const lastPreviousArchive: Archive = computed(() => previousArchives.value[previousArchives.value.length - 1])
// const additionalPreviousArchives: Array<Archive> = computed(() => previousArchives.value.filter((item) => item.id != lastPreviousArchive.value.id ))
// const hasAdditionalPrevious: boolean = computed(() => additionalPreviousArchives.value.length > 0)

export function getpreviousArchives (): Array<Archive> {
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
    return previousArchives.filter((item) => item.id != lastPreviousArchive.id )
}

export function hasAdditionalPrevious(): boolean {
    return getAdditionalPreviousArchives().length > 0
}
