<template>
  <div class="px-2 py-2 my-2 d-flex justify-content-between align-items-center project-column"
    :class="{ active: isActive }" @click.prevent="setupProject" @dblclick.prevent="enableEditMode"
    @mouseover="isHover = true" @mouseleave="isHover = false">
    <div class="d-flex align-items-center">
      <div v-if="!isEditMode" class="text-light fs-4 pe-1 me-1">
        <font-awesome-icon :icon="['fa', 'file']" />
      </div>
      <input ref="inputElement" v-else type="text" class="form-control" @blur="exitEditModeWithoutChange"
        @keyup.esc="exitEditModeWithoutChange" @keyup.enter="exitEditModeWithChange" :value="projectName" />
      <div v-if="!isEditMode" class="fw-semibold text-light project-name">
        {{ projectName }}
      </div>
    </div>
    <div v-if="!isHover" class="expire text-white-50">
      {{ leftDays }}
    </div>
    <button v-else type="button" class="btn text-light py-9" @click.stop="clickDeleteProjectButton">
      <font-awesome-icon :icon="['fas', 'trash']" />
    </button>
  </div>
</template>

<script setup lang="ts">
import type { Project } from '@/constants'
import { useAppStore, useModalStore, useProjectStore } from '@/stores/stores'
import moment from 'moment'
import { computed, ref, watch, type Ref } from 'vue'

const props = defineProps<{ project: Project }>()
const emit = defineEmits<{ deleteProject: [Project] }>()

const leftDays = computed(() =>
  props.project.expire_on ? `Expire ${moment.utc(props.project.expire_on).fromNow()}` : ''
)
const storeProject = useProjectStore()
const storeModal = useModalStore()
const isActive = computed(() => storeProject.lastProjectId == props.project.id)
const isEditMode = ref(false)
const isHover = ref(false)
const projectName = ref(props.project.name)
const inputElement: Ref<HTMLInputElement | null> = ref(null)
const storeApp = useAppStore()

watch(inputElement, (newElement) => {
  newElement?.focus()
})

function setupProject() {
  storeProject.setLastProjectId(props.project.id)
}

function enableEditMode() {
  isEditMode.value = true
}

async function exitEditModeWithChange(event: Event) {
  isEditMode.value = false
  projectName.value = event.target != null ? (event.target as HTMLInputElement).value : projectName.value
  await updateProjectName(props.project.id, projectName.value)
}

async function exitEditModeWithoutChange() {
  isEditMode.value = false
}

async function updateProjectName(projectId: string, newName: string) {
  const projectRequestData = {
    name: newName
  }
  try {
    await storeApp.axiosInstance.patch<Project>(`/projects/${projectId}`, projectRequestData)
  } catch (error: any) {
    console.log('Unable to update project name.', error, projectId)
    storeApp.alertsError(`Unable to update project name, project id: ${projectId}`)
  }
}

async function deleteProject() {
  try {
    await storeApp.axiosInstance.delete(`/projects/${props.project.id}`)
  } catch (error: any) {
    console.log('Unable to delete project.', error, props.project.id)
    storeApp.alertsError(`Unable to delete project, project id: ${props.project.id}`)
  }
  emit('deleteProject', props.project)
}

async function clickDeleteProjectButton() {
  storeModal.showModal(
    'Are you sure you want to delete:',
    'Delete',
    'Close',
    deleteProject,
    async () => { },
    [props.project.name]
  )
}
</script>

<style scoped>
.expire {
  font-size: 0.8em;
}

.active {
  background-color: orange;
}

.project-column {
  cursor: pointer;
  height: 3em;
}

.project-name {
  cursor: text;
}
</style>
