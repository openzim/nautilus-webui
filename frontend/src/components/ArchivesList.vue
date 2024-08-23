<template>
  <div>
    <div
      class="card m-5"
      :class="{ border: isActive, 'border-3': isActive, 'drag-active': isActive }"
      v-if="lastPreviousArchive"
    >
      <h4>
        <button type="button" class="btn text-secondary" @click.prevent="isShowed = !isShowed">
          <font-awesome-icon v-if="isShowed" :icon="['fas', 'minus']" />
          <font-awesome-icon v-else :icon="['fas', 'angle-down']" />
        </button>
        <span style="color: var(--main-color)">Created ZIM Files:</span>
      </h4>
      <LatestArchive :archive="lastPreviousArchive" />
      <p v-if="hasAdditionalPrevious && !isShowingAllPrevious">
        <a href="#" @click="showAllPrevious">View previous ZIM files</a>
      </p>
      <ul v-if="hasAdditionalPrevious && isShowingAllPrevious">
        <li v-for="archive in additionalPreviousArchives" v-bind:key="archive.id">
          {{ archive.config.filename }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import LatestArchive from '@/components/LatestArchive.vue'
import { ArchiveStatus, type Archive } from '@/constants'
import { useProjectStore } from '@/stores/stores'
import { ref, type Ref, computed } from 'vue'

const isActive = ref(false)
const isShowed = ref(true)
const isShowingAllPrevious = ref(false)

const storeProject = useProjectStore()
const previousArchives: Ref<Array<Archive>> = computed(() =>
  storeProject.lastProjectArchives.filter((item) => item.status != ArchiveStatus.PENDING)
)
const lastPreviousArchive: Ref<Archive> = computed(
  () => previousArchives.value[previousArchives.value.length - 1]
)
const additionalPreviousArchives: Ref<Array<Archive>> = computed(() =>
  previousArchives.value.filter((item) => item.id != lastPreviousArchive.value.id)
)
const hasAdditionalPrevious: Ref<boolean> = computed(() => additionalPreviousArchives.value.length > 0)

function showAllPrevious(event: Event) {
  event.preventDefault()
  isShowingAllPrevious.value = true
}
</script>
