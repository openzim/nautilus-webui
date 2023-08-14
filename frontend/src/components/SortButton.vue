<template>
  <button type="button" class="btn p-0" @click.prevent="updateCompareFunction">
    <span class="fw-bold">{{ props.title }}</span>
    <span class="mx-1">
      <font-awesome-icon :icon="['fas', 'sort']" />
    </span>
  </button>
</template>

<script setup lang="ts">
import { type CompareFunctionType } from '@/constants'
import { ref } from 'vue'
const isDecreased = ref(true)
const props = defineProps<{
  title: string
  increaseFunction: CompareFunctionType
  decreaseFunction: CompareFunctionType
}>()
const emit = defineEmits<{
  updateCompareFunction: [CompareFunctionType]
}>()

async function updateCompareFunction() {
  if (isDecreased.value) {
    emit('updateCompareFunction', props.decreaseFunction)
  } else {
    emit('updateCompareFunction', props.increaseFunction)
  }
  isDecreased.value = !isDecreased.value
}
</script>
