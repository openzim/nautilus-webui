<template>
  <div class="modal fade" tabindex="-1" ref="modal">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">{{ storeModal.title }}</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
            @click.prevent="storeModal.dismissModal"
          ></button>
        </div>
        <div class="modal-body">
          <ul>
            <li v-for="(element, key) in storeModal.content" :key="key">
              {{ element }}
            </li>
          </ul>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
            @click.prevent="clickButton(storeModal.clickSecondaryButton)"
          >
            {{ storeModal.secondaryButtonTitle }}
          </button>
          <button
            type="button"
            class="btn btn-primary"
            data-bs-dismiss="modal"
            @click.prevent="clickButton(storeModal.clickPrimaryButton)"
          >
            {{ storeModal.primaryButtonTitle }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useModalStore } from '@/stores/stores'
import * as bootstrap from 'bootstrap'
import { ref, watch, type Ref } from 'vue'

const storeModal = useModalStore()

const modal: Ref<Element | null> = ref(null)
defineExpose({ showModal })

watch(
  () => storeModal.isShown,
  (newValue) => {
    if (newValue) {
      showModal()
    }
  }
)

function showModal() {
  if (modal.value != null) {
    const confirmModal = new bootstrap.Modal(modal.value)
    confirmModal.show()
  }
}

function clickButton(action: () => Promise<void>) {
  storeModal.dismissModal()
  action()
}
</script>
