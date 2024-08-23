<template>
  <div style="text-align: center">
    <div v-if="canBeDownloaded">
      <a :href="props.archive.download_url" download
        >[Download {{ props.archive.config.filename }} ({{ archiveFileSize }})]</a
      >
      <br />
      <span>created on {{ formattedDate(props.archive.created_on) }}</span>
    </div>
    <div v-else>
      <span class="unavail-zim"
        >[Download {{ props.archive.config.filename }} ({{ archiveFileSize }} of files]</span
      >
      <br />
      <span>requested on {{ humanRequestedOn }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArchiveStatus, type Archive, humanifyFileSize } from '@/constants'
import { computed, type Ref } from 'vue'
import { DateTime } from 'luxon'

const props = defineProps<{ archive: Archive }>()

const canBeDownloaded: Ref<boolean> = computed(() => props.archive.status == ArchiveStatus.READY)
const archiveFileSize: Ref<string> = computed(() => humanifyFileSize(props.archive.filesize!))
const humanRequestedOn: Ref<string> = computed(() =>
  props.archive.requested_on ? formattedDate(props.archive.requested_on) : '-'
)

function formattedDate(date: string): string {
  return DateTime.fromISO(date).toLocaleString(DateTime.DATETIME_MED_WITH_WEEKDAY)
}
</script>

<style type="text/css">
.unavail-zim {
  color: black;
  font-weight: bold;
}
</style>
