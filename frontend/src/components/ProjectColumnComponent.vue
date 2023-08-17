<template>
  <div class="px-2 py-2 my-2 d-flex justify-content-between align-items-center border" :class="{ 'active': isActive }"
    @click.prevent="setupProject" @dblclick.prevent="enableEditMode">
    <div class="d-flex align-items-center ">
      <div v-if="!isEditMode" class="text-light fs-4 pe-1 me-1">
        <font-awesome-icon :icon="['fa', 'file']" />
      </div>
      <input ref="inputElement" v-else type="text" class="form-control" v-model="projectName" @blur="disableEditMode">
      <div v-if="!isEditMode" class="fw-semibold text-light">
        {{ projectName }}
      </div>
    </div>
    <div class="expire text-white-50">
      {{ leftDays }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Project } from '@/constants';
import { useAppStore, useProjectIdStore } from '@/stores/stores';
import moment from 'moment';
import { computed, ref, watch, type Ref } from 'vue';
const props = defineProps<{ project: Project }>()
const leftDays = computed(() => props.project.expire_on ? `Expire ${moment.utc(props.project.expire_on).fromNow()}` : '')
const storeProjectId = useProjectIdStore()
const isActive = computed(() => storeProjectId.projectId == props.project.id)
const isEditMode = ref(false)
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

async function disableEditMode() {
  isEditMode.value = false
  await updateProjectName(props.project.id, projectName.value)
}

async function updateProjectName(projectId: string, newName: string) {
  const projectRequestData = {
    name: newName
  }
  try {
    await storeApp.axiosInstance.patch<Project>(
      `/projects/${projectId}`,
      projectRequestData
    )
  } catch (error: any) {
    console.log('Unable to update project name.', error, projectId)
    storeApp.alertsError(`Unable to update project name, project id: ${projectId}`)
  }
}
</script>

<style scoped>
.expire {
  font-size: 0.8em;
}

.active {
  background-color: orange;
}
</style>
