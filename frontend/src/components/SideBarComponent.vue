<template>
  <div class="d-flex flex-column" style="height: 100%">
    <div class="d-flex justify-content-between mt-2 border-bottom border-2 border-white">
      <div class="fw-bold fs-4 text-light">Collection:</div>
      <button
        type="button"
        class="btn fw-bold fs-5 text-light p-1"
        @click.prevent="createAndUpdateProject"
      >
        <font-awesome-icon :icon="['fas', 'plus']" />
      </button>
    </div>
    <div class="flex-grow-1 py-2 overflow-x-auto">
      <ProjectColumnComponent
        v-for="project in storeProject.projects"
        :key="project.id"
        :project="project"
        @delete-project="removeProjectFromList"
      />
    </div>
    <div class="border-top border-2 border-white py-2">
      <p class="text-light"><router-link to="/faq" class="link-light">FAQ</router-link></p>
      <p class="text-light"><router-link to="/contact" class="link-light">Contact</router-link></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import ProjectColumnComponent from './ProjectColumnComponent.vue'
import type { Project } from '@/constants'
import { useProjectStore } from '@/stores/stores'
import { createNewProject, updateProjects } from '@/utils'
const storeProject = useProjectStore()

await updateProjects()

async function createAndUpdateProject() {
  let new_project = await createNewProject('New Project')
  if (new_project) {
    await updateProjects()
    storeProject.setLastProjectId(new_project.id)
  }
}

function removeProjectFromList(project: Project) {
  storeProject.setProjects(storeProject.projects.filter((element) => element.id != project.id))
  if (storeProject.projects.length != 0) {
    storeProject.setLastProjectId(storeProject.projects[0].id)
  } else {
    storeProject.clearLastProjectId()
  }
}
</script>
