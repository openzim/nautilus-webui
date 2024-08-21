<template>
  <div class="meta-container rounded-2 border border-1">
    <div class="d-flex flex-row-reverse">
      <div class="btn-group btn-group-sm custom-btn-outline-primary" role="group">
        <label class="btn btn-outline-primary" for="toggle-metadata-edit" :class="{ active: inMetadataEditMode }">
          <input
            type="radio"
            class="btn-check"
            name="btnradio"
            id="toggle-metadata-edit"
            autocomplete="off"
            @click.prevent="inMetadataEditMode = true"
            :checked="inMetadataEditMode"
          />
          Edit
        </label>

        <label class="btn btn-outline-primary" for="toggle-metadata-preview" :class="{ active: !inMetadataEditMode }">
          <input
            type="radio"
            class="btn-check"
            name="btnradio"
            id="toggle-metadata-preview"
            autocomplete="off"
            @click.prevent="exitMetadataEditModeHandler"
            :checked="!inMetadataEditMode"
          />
          Preview
        </label>
      </div>
    </div>
    <form :onsubmit="eatEvent">
    <div class="row" v-if="inMetadataEditMode">
      <p><input class="form-control" type="text" name="zim-title" @change="updatedField" v-model="archiveMetadataFormModal.title" placeholder="ZIM Title metadata" /></p>
      <p><input class="form-control" type="text" name="zim-description" @change="updatedField" v-model="archiveMetadataFormModal.description" placeholder="ZIM Description metadata" /></p>
      <p><input class="form-control" type="text" name="zim-name" @change="updatedField" v-model="archiveMetadataFormModal.name" placeholder="ZIM Name metadata" /></p>
      <p><input class="form-control" type="text" name="zim-creator" @change="updatedField" v-model="archiveMetadataFormModal.creator" placeholder="ZIM Creator metadata" /></p>
      <p><input class="form-control" type="text" name="zim-lang" @change="updatedField" v-model="archiveMetadataFormModal.languages" placeholder="ZIM Language metadata" /></p>
      <p><smart-tagz
            autosuggest
            editable
            inputPlaceholder="ZIM Tags"
            :default-tags="archiveMetadataFormModal.tags"
            :onChanged="results => archiveMetadataFormModal.tags = results"
            :allowPaste="{delimiter: ','}"
            :allowDuplicates="false"
        />
      </p>
      <p><input class="form-control" type="file" @change="updatedIllustration" placeholder="ZIM Illustration (48x48px PNG)" /></p>
      <p><input class="form-control" type="text" name="zim-filename" @change="updatedField" v-model="archiveMetadataFormModal.filename" placeholder="ZIM Filename" /></p>
    </div>
    <div class="row" v-else>
      <div class="col">
        <img :src="'data:image/png;base64,' + archiveMetadataFormModal.illustration" class="rounded-2 border-0" />
      </div>
      <div class="col">
        <div class="row">Title: {{ archiveMetadataFormModal.title }}</div>
        <div class="row">Description: {{ archiveMetadataFormModal.description }}</div>
        <div class="row">Name: {{ archiveMetadataFormModal.name }}</div>
        <div class="row">Creator: {{ archiveMetadataFormModal.creator }}</div>
        <div class="row">Language: {{ archiveMetadataFormModal.languages }}</div>
        <div class="row">Tags: {{ archiveMetadataFormModal.tags }}</div>
        <div class="row">
          <div class="col">Filename: {{ archiveMetadataFormModal.filename }}</div>
          <div class="col">Name: {{ archiveMetadataFormModal.name }}</div>
        </div>
      </div>
    </div>
    <p><input class="form-control" type="email" @change="updatedField" v-model="email" placeholder="What's your email?" name="email" /></p>
    <p><button class="btn btn-primary" :disabled="inMetadataEditMode" @click.prevent="requestZIM">ZIM it!</button></p>
    </form>
  </div>
</template>
<script setup lang="ts">

import { computed, ref, watch, type Ref } from 'vue'
import { storeToRefs } from 'pinia'
import { type ArchiveMetadataFormType  } from '@/constants'
import { useAppStore, useModalStore, useProjectStore } from '@/stores/stores'
import { refreshArchives, updateProjects } from '@/utils'
import { getLastPreviousArchive } from '@/commons'
import { SmartTagz } from "smart-tagz";
import "smart-tagz/dist/smart-tagz.css";

const storeApp = useAppStore()
const storeProject = useProjectStore()
const storeModal = useModalStore()
const { lastProjectPendingArchive } = storeToRefs(storeProject)

let inMetadataEditMode = ref(false)
let tag: string = ""
let tags = []


function eatEvent(e) {
  e.preventDefault()
}

function updatedField() {
  console.debug('## UPDATED ##')
  // emit('updateArchiveMetadata', archiveMetadataFormModal.value)
}


const imageDimensions = dataUrl => 
  new Promise((resolve, reject) => {
      const img = new Image()

      // the following handler will fire after a successful loading of the image
      img.onload = () => {
        const { naturalWidth: width, naturalHeight: height } = img
        resolve({ width, height })
      }

      // and this handler will fire if there was an error with the image (like if it's not really an image or a corrupted one)
      img.onerror = () => {
        reject('failed to load image')
      }

      img.src = dataUrl
})

function updatedIllustration(ev) {
  console.debug('updatedIllustration')
  const file = ev.target.files[0];
  const reader = new FileReader();
  if (!file) {
    console.error('updatedIllustration failed without file')
    return
  }
  console.debug('file', file)

  reader.onload = async (e) => {
    console.log('onload')
    let [prefix, bytes] = reader.result.split(',', 2)
    let mimetype = prefix.replace(RegExp('^data:(.+);base64$'), '$1')
    if (mimetype != 'image/png') {
      console.error('Illustration is not a PNG Image', mimetype)
      storeApp.alertsError(`Illustration must be a 48x48px PNG Image (not ${mimetype})`)
      return
    }

    // load on DOM to get dimensions
    const dimensions = {width: 0, height: 0}
    await imageDimensions(reader.result)
      .then(function(dim) {
        dimensions.width = dim.width, dimensions.height = dim.height
      })
      .catch(function(err) {
          console.error('Illustration could not be loaded as image', error)
          storeApp.alertsError('Illustration must be a 48x48px PNG Image (failed to load)')
      })

    if (!dimensions.width || !dimensions.height){
      console.log('failed to load', dimensions)
      return
    }

    if (dimensions.width != 48 || dimensions.height != 48) {
      console.error('Illustration dimensions are incorrect', dimensions)
      storeApp.alertsError(`Illustration must be a 48x48px PNG Image (not ${dimensions.width}x${dimensions.height}px)`)
      return
    }

    archiveMetadataFormModal.value.illustration = bytes
    console.info('updated illus data:', reader.result)
  }
  reader.readAsDataURL(file);
}

function formModalFromArchive() {
  console.log('archive?', storeProject.lastProjectPendingArchive)

  let lastPreviousArchive = getLastPreviousArchive()
  if (lastPreviousArchive) {
    return {
      title: lastPreviousArchive.config.title,
      description: lastPreviousArchive.config.description,
      name: lastPreviousArchive.config.name,
      publisher: lastPreviousArchive.config.publisher,
      creator: lastPreviousArchive.config.creator,
      languages: lastPreviousArchive.config.languages,
      tags: lastPreviousArchive.config.tags ,
      illustration: lastPreviousArchive.config.illustration,
      filename: lastPreviousArchive.config.filename,
    }
  }

  if (!storeProject.lastProjectPendingArchive) {
    return {}
  }
  return {
    title: storeProject.lastProjectPendingArchive.config.title || '',
    description: storeProject.lastProjectPendingArchive.config.description || '',
    name: storeProject.lastProjectPendingArchive.config.name || '${storeProject.lastProject.name}',
    publisher: storeProject.lastProjectPendingArchive.config.publisher || 'nautilus by openZIM',
    creator: storeProject.lastProjectPendingArchive.config.creator || '',
    languages: storeProject.lastProjectPendingArchive.config.languages || 'eng',
    tags: storeProject.lastProjectPendingArchive.config.tags  || [],
    illustration: storeProject.lastProjectPendingArchive.config.illustration || 'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwAQMAAABtzGvEAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAANQTFRFR3BMgvrS0gAAAAF0Uk5TAEDm2GYAAAANSURBVBjTY2AYBdQEAAFQAAGn4toWAAAAAElFTkSuQmCC',
    filename: storeProject.lastProjectPendingArchive.config.filename || `${storeProject.lastProject.name}.zim`,
  }
}

const archiveMetadataFormModal: Ref<ArchiveMetadataFormType> = ref(formModalFromArchive())
const email: Ref<string> = ref('')

watch(lastProjectPendingArchive, async () => {
  console.debug("archive update in store, updating form")
  archiveMetadataFormModal.value = formModalFromArchive()
})


const emit = defineEmits<{
  updateArchiveMetadata: [MetadataEditorFormType]
}>()

// watch(
//   archiveMetadataFormModal,
//   async (newValue) => {
//     console.debug("!!form update", newValue)
//     emit('updateArchiveMetadata', newValue)
//   },
//   { deep: true }
// )

async function actuallyUpdateMetadata() {
  // online stuff
  const archivePatchData = {
    email: archiveMetadataFormModal.value.email,
    config: {
      title: archiveMetadataFormModal.value.title,
      description: archiveMetadataFormModal.value.description,
      name: archiveMetadataFormModal.value.name,
      publisher: archiveMetadataFormModal.value.publisher,
      creator: archiveMetadataFormModal.value.creator,
      languages: archiveMetadataFormModal.value.languages,
      tags: archiveMetadataFormModal.value.tags,
      illustration: archiveMetadataFormModal.value.illustration,
      filename: archiveMetadataFormModal.value.filename,
    }
  }
  try {
    const response = await storeApp.axiosInstance.patch<string>(`/projects/${storeProject.lastProjectId}/archives/${storeProject.lastProjectPendingArchive.id}`, archivePatchData)
    console.debug(response.data)
  } catch (error: unknown) {
    console.log('Unable to update archive metadata', error)
    storeApp.alertsError('Unable to update archive metadata')
  }
  inMetadataEditMode.value = false
  // reload data from online?
  refreshArchives()
}

async function requestZIM() {
  console.log('lets GO!')
  try {
    const response = await storeApp.axiosInstance.post<string>(`/projects/${storeProject.lastProjectId}/archives/${storeProject.lastProjectPendingArchive.id}/request`)
    console.debug(response.data)
    refreshArchives()
  } catch (error: unknown) {
    console.log('Unable to request archive', error)
    storeApp.alertsError('Failed to request archive')
  }
}

async function exitMetadataEditModeHandler() {
  if (!inMetadataEditMode.value) {
    return
  }
  storeModal.showModal(
    'Are you sure you want to update Metadata?',
    'Change',
    'Discard',
    actuallyUpdateMetadata,
    async () => {
      inMetadataEditMode.value = false
    }
  )
}

</script>
<style scoped>
  .meta-container {
    width: 50em;
    background-color: #fdfdfd;
  }

  img {
    width: 6em;
    height: 6em;
    background-color: #d9d9d9;
  }
</style>
