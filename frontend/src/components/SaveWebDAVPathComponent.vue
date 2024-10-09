<template>
  <div class="card m-5 card-body justify-content-between align-items-baseline">
    <div>
      <label for="webdavPathInput" class="form-label">Set WebDAV Path</label>
      <p class="form-text">
        This project is not yet associated with a folder on the target WebDAV drive. <br />Please
        enter of paste the path or URL for this project within
        <a target="_blank" :href="storeApp.constants.env.NAUTILUS_STORAGE_URL">{{
          storeApp.constants.env.NAUTILUS_STORAGE_URL
        }}</a
        >.
      </p>
      <input
        class="form-control"
        id="webdavPathInput"
        type="text"
        placeholder="my-folder/sub-folder"
        v-model="webdav_path"
        aria-describedby="webdavPathHelp"
        @keyup.enter="set_webdav_path"
      />
      <p class="form-text" id="webdavPathHelp">
        <strong>Note</strong>: empty value is valid (means root folder)
      </p>
    </div>
    <button
      class="btn btn-outline-primary"
      :disabled="!isValidWebDAVPathInput"
      @click.prevent="set_webdav_path"
    >
      Set WebDAV path
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, type Ref } from 'vue'
import sanitize from 'sanitize-filename'
import { useAppStore } from '@/stores/stores'
import { set_project_webdav_path } from '@/utils'

const storeApp = useAppStore()
const webdav_path: Ref<string | null> = ref(null)

const emit = defineEmits<{ updatedWebdav: [webdav_path: string | null] }>()

const busyRefreshing: Ref<boolean> = ref(false)

function isValidHttpUrl(text: string): boolean {
  let url: URL

  try {
    url = new URL(text)
  } catch (_) {
    return false
  }
  return url.protocol === 'http:' || url.protocol === 'https:'
}

const isValidWebDAVPathInput: Ref<boolean> = computed(function () {
  if (busyRefreshing.value) {
    return false
  }
  if (!webdav_path.value) {
    return false
  }
  let text = String(webdav_path.value)
  if (isValidHttpUrl(text)) {
    if (text.indexOf(storeApp.constants.env.NAUTILUS_STORAGE_URL) != 0) {
      return false
    }
    text = new URL(text).pathname
  }
  try {
    return text == sanitizeWebDAVPath(text)
  } catch (_) {
    return false
  }
})

function sanitizeWebDAVPath(path: string) {
  if (isValidHttpUrl(path)) {
    if (path.indexOf(storeApp.constants.env.NAUTILUS_STORAGE_URL) != 0) {
      throw Error("WebDAV Path is an URL that's not part of drive")
    }
    path = new URL(path).pathname
  }
  return path
    .split('/')
    .map((part) => sanitize(part))
    .join('/')
    .replaceAll(/\/+/g, '/')
}

async function set_webdav_path() {
  if (webdav_path.value === null) return
  try {
    webdav_path.value = sanitizeWebDAVPath(webdav_path.value)
  } catch (error) {
    console.error('Unable to set WebDAV path', error)
    return
  }
  busyRefreshing.value = true
  let returnedWebdavPath: string | null = await set_project_webdav_path(webdav_path.value)
  busyRefreshing.value = false
  emit('updatedWebdav', returnedWebdavPath)
}
</script>

<style type="text/css">
label {
  color: var(--main-color);
  opacity: 0.6;
}
</style>
