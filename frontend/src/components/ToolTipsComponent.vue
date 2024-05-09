<template>
  <div
    ref="element"
    data-bs-toggle="tooltip"
    :data-bs-title="props.title"
    style="width: fit-content"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { type Ref, onBeforeUnmount, onMounted, ref } from 'vue'
import { Tooltip } from 'bootstrap'

const props = defineProps<{
  title: string | undefined
}>()
const element: Ref<Element | null> = ref(null)
const tootip: Ref<Tooltip | null> = ref(null)
onMounted(() => {
  tootip.value = new Tooltip(element.value!)
})
onBeforeUnmount(() => {
  tootip.value?.dispose()
})
</script>
