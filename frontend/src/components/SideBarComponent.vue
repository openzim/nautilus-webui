<template>
  <div class="d-flex flex-column" style="height: 100%;">
    <div class="d-flex justify-content-between mt-2 border-bottom border-2 border-white ">
      <div class="fw-bold fs-4 text-light">Collection:</div>
      <button type="button" class="btn fw-bold fs-5 text-light p-1">
        <font-awesome-icon :icon="['fas', 'plus']" />
      </button>
    </div>
    <div class="flex-grow-1 py-2">
      Holder
    </div>
    <div class="border-top border-2 border-white py-2">
      <p class="text-light">FAQ</p>
      <p class="text-light">Contact</p>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>
