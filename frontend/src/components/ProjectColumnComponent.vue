<template>
  <div class="px-2 py-2 my-2 d-flex justify-content-between align-items-center project-column"
    :class="{ active: isActive }" @click.prevent="setupProject" @dblclick.prevent="enableEditMode"
    @mouseover="isHover = true" @mouseleave="isHover = false">
    <div class="d-flex align-items-center">
      <div v-if="!isEditMode" class="text-light fs-4 pe-1 me-1">
        <font-awesome-icon :icon="['fa', 'file']" />
      </div>
      <input ref="inputElement" v-else type="text" class="form-control" v-model="projectName"
        @blur="exitEditModeWithChange" @keyup.esc="exitEditModeWithoutChange" @keyup.enter="exitEditModeWithChange" />
      <div v-if="!isEditMode" class="fw-semibold text-light">
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
import { useAppStore, useModalStore, useProjectIdStore } from '@/stores/stores'
import moment from 'moment'
import { computed, ref, watch, type Ref } from 'vue'

const props = defineProps<{ project: Project }>()
const emit = defineEmits<{ deleteProject: [Project] }>()

const leftDays = computed(() =>
  props.project.expire_on ? `Expire ${moment.utc(props.project.expire_on).fromNow()}` : ''
)
const storeProjectId = useProjectIdStore()
const storeModal = useModalStore()
const isActive = computed(() => storeProjectId.projectId == props.project.id)
const isEditMode = ref(false)
const isHover = ref(false)
const projectName = ref(props.project.name)
const inputElement: Ref<HTMLInputElement | null> = ref(null)
const storeApp = useAppStore()

watch(inputElement, (newElement) => {
  newElement?.focus()
})

function setupProject() {
  storeProjectId.setProjectId(props.project.id)
}

function enableEditMode() {
  isEditMode.value = true
}

async function exitEditModeWithChange() {
  isEditMode.value = false
  await updateProjectName(props.project.id, projectName.value)
}

async function exitEditModeWithoutChange() {
  isEditMode.value = false
  projectName.value = props.project.name
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
  const toBeDeletedProject = props.project
  if (isActive.value) {
    storeProjectId.clearProjectId()
  }
  try {
    await storeApp.axiosInstance.delete(`/projects/${toBeDeletedProject.id}`)
  } catch (error: any) {
    console.log('Unable to delete project.', error, props.project.id)
    storeApp.alertsError(`Unable to delete project, project id: ${props.project.id}`)
  }
  emit('deleteProject', toBeDeletedProject)
}

async function clickDeleteProjectButton() {
  storeModal.showModal("Are you sure you want to delete:", "Delete", "Close", deleteProject, async () => { }, [props.project.name])
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
</style>
