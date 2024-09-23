<template>
  <div class="card m-5 card-body d-flex justify-content-between align-items-baseline">
    <div>
      <label for="webdavPathInput" class="form-label">WebDAV Link</label>
      <p class="form-text">This project is linked to path <a target="_blank" :href="webdav_url"><code>{{ webdav_path }}/</code></a>.</p>
      <p><button class="btn btn-sm btn-outline-secondary" :disabled="!canRefresh" @click.prevent="set_webdav_path">Refresh from WebDAV path</button></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore, useProjectStore } from '@/stores/stores'
import { set_project_webdav_path } from '@/utils.ts'
import { storeToRefs } from 'pinia'

const storeProject = useProjectStore()
const storeApp = useAppStore()
const busyRefreshing: Ref<boolean> = ref(false)

const canRefresh: boolean = computed(function() {
  return busyRefreshing.value ? false : webdav_path !== null
})

const { lastProject } = storeToRefs(storeProject)

const webdav_path = computed(function() {
  if (!lastProject.value)
    return null
  return lastProject.value.webdav_path || null
})
const webdav_url = computed(function() {
  return webdav_path.value ? `${storeApp.constants.env.NAUTILUS_STORAGE_URL}${webdav_path.value}`: null
})

async function set_webdav_path(event: Event) {
  busyRefreshing.value = true
  await set_project_webdav_path(webdav_path.value)
  busyRefreshing.value = false
}
</script>

<style type="text/css">
  label {
    color: var(--main-color);
    opacity: 0.6;
  }
</style>
