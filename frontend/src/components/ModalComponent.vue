<template>
  <div class="modal fade show" tabindex="-1" ref="modal">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">{{ props.title }}</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <slot />
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
            @click.prevent="emit('clickSecondaryButton')"
          >
            {{ props.secondaryButtonTitle }}
          </button>
          <button
            type="button"
            class="btn btn-primary"
            data-bs-dismiss="modal"
            @click.prevent="emit('clickPrimaryButton')"
          >
            {{ props.primaryButtonTitle }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as bootstrap from 'bootstrap'
import { ref, type Ref } from 'vue'

const props = defineProps<{
  title: string
  primaryButtonTitle: string
  secondaryButtonTitle: string
}>()
const emit = defineEmits<{
  clickPrimaryButton: []
  clickSecondaryButton: []
}>()
const modal: Ref<Element | null> = ref(null)
defineExpose({ showModal })

function showModal() {
  if (modal.value != null) {
    const confirmModal = new bootstrap.Modal(modal.value)
    confirmModal.show()
  }
}
</script>
