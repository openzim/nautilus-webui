<template>
  <!-- Alert messages should be above all other elements -->
  <div class="position-absolute top-0 end-0 mt-1 me-1" style="z-index: 9999">
    <div v-for="[key, item] in storeApp.alertMessages" :key="key">
      <div class="alert px-1" :class="'alert-' + item.type" role="alert">
        <div class="container">
          <div class="row justify-content-between">
            <div class="col-md-auto">
              {{ item.message }}
            </div>
            <div class="col-md-auto">
              <button type="button" class="btn p-0" @click="storeApp.clearError(key)">
                <font-awesome-icon :icon="['fas', 'xmark']" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/stores'

const storeApp = useAppStore()
</script>
