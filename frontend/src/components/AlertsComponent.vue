<template>
  <div class="position-absolute top-0 end-0 mt-1 me-1">
    <div
      class="alert alert-danger px-1"
      role="alert"
      v-for="[key, message] in storeApp.errorMessgae"
      :key="key"
    >
      <div class="container">
        <div class="row justify-content-between">
          <div class="col-md-auto">
            {{ message }}
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
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/stores'

const storeApp = useAppStore()
</script>
