<template>
  <div class="card m-5 card-body d-flex justify-content-between align-items-baseline">
    <div>
      <label for="webdavPathInput" class="form-label">Set WebDAV Path</label>
      <p class="form-text">This project is not yet associated with a folder on the target WebDAV drive.
        <br />Please enter of paste the path or URL for this project within xxx.</p>
      <input class="form-control" id="webdavPathInput" type="text" placeholder="my-folder/sub-folder" v-model="webdav_path" aria-describedby="webdavPathHelp" />
      <p class="form-text" id="webdavPathHelp"><strong>Note</strong>: empty value is valid (means root folder)</p>
    </div>
    <button class="btn btn-outline-primary" :disabled="!webdav_path" @click.prevent="set_webdav_path">Set WebDAV path</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAppStore, useProjectStore } from '@/stores/stores'
import updateProjects from '@/utils.ts'

const storeApp = useAppStore()
const storeProject = useProjectStore()
const webdav_path: Ref<string> = ref(null)

const emit = defineEmits<{
  // dropFilesHandler: [files: FileList, uploadFileSize: number]
  // updateIsActive: [newValue: boolean]
}>()


async function set_webdav_path(event: Event) {
  console.log(`Setting WebDAV path to ${webdav_path.value}`)

  const requestData = {'webdav_path': webdav_path.value}
  console.debug(requestData)

  storeApp.axiosInstance
    .post<File>(`/projects/${storeProject.lastProjectId}.dav`, requestData)
    .then((response) => {
      storeProject.replaceProject(response.data)
      storeApp.alertsSuccess(`Successfuly set WebDAV path`)
    })
    .catch((error) => {
      console.error(error)
      storeApp.alertsError(`Unable to set WebDAV path`)
    })

  // updateProjects()
}
</script>

<style type="text/css">
  label {
    color: var(--main-color);
    opacity: 0.6;
  }
</style>
