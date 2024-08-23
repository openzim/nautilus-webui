<template>
  <div class="meta-container rounded-2 border border-1 p-3">
    <div class="d-flex flex-row-reverse">
      <div class="btn-group btn-group-sm custom-btn-outline-primary" role="group">
        <label
          class="btn btn-outline-primary"
          for="toggle-metadata-edit"
          :class="{ active: inMetadataEditMode }"
        >
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

        <label
          class="btn btn-outline-primary"
          for="toggle-metadata-preview"
          :class="{ active: !inMetadataEditMode }"
        >
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
        <p>
          <input
            class="form-control"
            type="text"
            name="zim-title"
            required
            v-model="archiveMetadataFormModal.title"
            placeholder="ZIM Title metadata"
          />
        </p>
        <p>
          <input
            class="form-control"
            type="text"
            name="zim-description"
            required
            v-model="archiveMetadataFormModal.description"
            placeholder="ZIM Description metadata"
          />
        </p>
        <p>
          <input
            class="form-control"
            type="text"
            name="zim-name"
            required
            v-model="archiveMetadataFormModal.name"
            placeholder="ZIM Name metadata"
          />
        </p>
        <p>
          Illustration (48x48px PNG):
          <ImageUpload
            :value="archiveMetadataFormModal.illustration"
            enforced_format="png"
            :enforced_dimensions="{ width: 48, height: 49 }"
            style="width: 48px; height: 48px"
            @change="onIllustrationUpdate"
          />
        </p>
        <p>
          Main logo (horizontal PNG):
          <ImageUpload
            :value="archiveMetadataFormModal.main_logo"
            enforced_format="png"
            style="height: 4rem; max-width: 24rem"
            @change="onMainlogoUpdate"
          />
        </p>
        <p>
          <input
            class="form-control"
            type="text"
            name="zim-creator"
            required
            v-model="archiveMetadataFormModal.creator"
            placeholder="ZIM Creator metadata"
          />
        </p>
        <p>
          <input
            class="form-control"
            type="text"
            name="zim-lang"
            required
            v-model="archiveMetadataFormModal.languages"
            placeholder="ZIM Language metadata"
          />
        </p>
        <p>
          <smart-tagz
            autosuggest
            editable
            inputPlaceholder="ZIM Tags"
            :default-tags="archiveMetadataFormModal.tags"
            :onChanged="(results: string[]) => (archiveMetadataFormModal.tags = results)"
            :allowPaste="{ delimiter: ',' }"
            :allowDuplicates="false"
          />
        </p>
        <p>
          <input
            class="form-control"
            type="text"
            required
            name="zim-filename"
            v-model="archiveMetadataFormModal.filename"
            placeholder="ZIM Filename"
          />
        </p>
      </div>
      <div class="row" v-else>
        <div>Title: {{ archiveMetadataFormModal.title }}</div>
        <div>Description: {{ archiveMetadataFormModal.description }}</div>
        <div>Name: {{ archiveMetadataFormModal.name }}</div>
        <div>
          Illustration:
          <img
            :src="'data:image/png;base64,' + archiveMetadataFormModal.illustration"
            class="rounded-2 border-0 illustration"
          />
        </div>
        <div>
          Logo:
          <img
            :src="'data:image/png;base64,' + archiveMetadataFormModal.main_logo"
            class="border-0 main-logo"
          />
        </div>
        <div>Creator: {{ archiveMetadataFormModal.creator }}</div>
        <div>Language: {{ archiveMetadataFormModal.languages }}</div>
        <div>
          Tags:
          <span
            v-for="tag in archiveMetadataFormModal.tags"
            v-bind:key="tag"
            class="badge rounded-pill text-bg-secondary me-1"
            >{{ tag }}</span
          >
        </div>
        <div>Filename: {{ archiveMetadataFormModal.filename }}</div>
      </div>
      <p>
        <input
          class="form-control"
          type="email"
          v-model="archiveMetadataFormModal.email"
          placeholder="What's your email?"
          name="email"
        />
      </p>
      <p>
        <button class="btn btn-primary" :disabled="inMetadataEditMode" @click.prevent="requestZIM">
          ZIM it!
        </button>
      </p>
    </form>
  </div>
</template>
<script setup lang="ts">
import { ref, watch, type Ref } from 'vue'
import { storeToRefs } from 'pinia'
import { type ArchiveMetadataFormType, DEFAULT_ILLUSTRATION, DEFAULT_MAIN_LOGO } from '@/constants'
import { useAppStore, useModalStore, useProjectStore } from '@/stores/stores'
import { refreshArchives } from '@/utils'
import { getLastPreviousArchive } from '@/commons'
// @ts-ignore
import { SmartTagz } from 'smart-tagz'
import 'smart-tagz/dist/smart-tagz.css'
import ImageUpload from '@/components/ImageUpload.vue'

const storeApp = useAppStore()
const storeProject = useProjectStore()
const storeModal = useModalStore()
const { lastProjectPendingArchive } = storeToRefs(storeProject)

let inMetadataEditMode = ref(false)

function eatEvent(event: Event) {
  event.preventDefault()
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
      tags: lastPreviousArchive.config.tags,
      illustration: lastPreviousArchive.config.illustration,
      main_logo: lastPreviousArchive.config.main_logo,
      filename: lastPreviousArchive.config.filename,
      email: lastPreviousArchive.email ? lastPreviousArchive.email : ''
    }
  }

  if (!storeProject.lastProjectPendingArchive) {
    return {}
  }
  return {
    title: storeProject.lastProjectPendingArchive.config.title || '',
    description: storeProject.lastProjectPendingArchive.config.description || '',
    name:
      storeProject.lastProjectPendingArchive.config.name || storeProject.lastProject === null
        ? ''
        : `${storeProject.lastProject.name}`,
    publisher: storeProject.lastProjectPendingArchive.config.publisher || 'nautilus by openZIM',
    creator: storeProject.lastProjectPendingArchive.config.creator || '',
    languages: storeProject.lastProjectPendingArchive.config.languages || 'eng',
    tags: storeProject.lastProjectPendingArchive.config.tags || [],
    illustration:
      storeProject.lastProjectPendingArchive.config.illustration || DEFAULT_ILLUSTRATION,
    main_logo: storeProject.lastProjectPendingArchive.config.main_logo || DEFAULT_MAIN_LOGO,
    filename: storeProject.lastProjectPendingArchive.config.filename || `nautilus.zim`,
    email: storeProject.lastProjectPendingArchive.config.email || ''
  }
}

// @ts-ignore
const archiveMetadataFormModal: Ref<ArchiveMetadataFormType> = ref(formModalFromArchive())

watch(lastProjectPendingArchive, async () => {
  console.debug('archive update in store, updating form')
  // @ts-ignore
  archiveMetadataFormModal.value = formModalFromArchive()
})

async function actuallyUpdateMetadata() {
  // online stuff
  const archivePatchData = {
    email: archiveMetadataFormModal.value.email || '',
    config: {
      title: archiveMetadataFormModal.value.title,
      description: archiveMetadataFormModal.value.description,
      name: archiveMetadataFormModal.value.name,
      publisher: archiveMetadataFormModal.value.publisher,
      creator: archiveMetadataFormModal.value.creator,
      languages: archiveMetadataFormModal.value.languages,
      tags: archiveMetadataFormModal.value.tags,
      illustration: archiveMetadataFormModal.value.illustration,
      main_logo: archiveMetadataFormModal.value.main_logo,
      filename: archiveMetadataFormModal.value.filename
    }
  }
  try {
    if (storeProject.lastProjectId === null || storeProject.lastProjectPendingArchive === null)
      throw 'missing IDs'
    const response = await storeApp.axiosInstance.patch<string>(
      `/projects/${storeProject.lastProjectId}/archives/${storeProject.lastProjectPendingArchive.id}`,
      archivePatchData
    )
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
  const archivePostData = { email: archiveMetadataFormModal.value.email || '' }
  try {
    if (storeProject.lastProjectId === null || storeProject.lastProjectPendingArchive === null)
      throw 'missing IDs'
    const response = await storeApp.axiosInstance.post<string>(
      `/projects/${storeProject.lastProjectId}/archives/${storeProject.lastProjectPendingArchive.id}/request`,
      archivePostData
    )
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
    },
    []
  )
}

function onIllustrationUpdate(data: string) {
  archiveMetadataFormModal.value.illustration = data
}
function onMainlogoUpdate(data: string) {
  archiveMetadataFormModal.value.main_logo = data
}
</script>
<style scoped>
.meta-container {
  width: 50em;
  background-color: #fdfdfd;
}

img.illustration {
  width: 48px;
  height: 48px;
}

img.main-logo {
  height: 4rem;
}
</style>
