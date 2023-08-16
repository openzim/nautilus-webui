<template>
  <div class="px-2 py-2 my-2 d-flex justify-content-between align-items-center border">
    <div class="d-flex align-items-center ">
      <div class="text-light fs-4 pe-1 me-1">
        <font-awesome-icon :icon="['fa', 'file']" />
      </div>
      <div class="fw-semibold text-light">
        {{ props.project.name }}
      </div>
    </div>
    <div class="expire text-white-50">
      {{ leftDays }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Project } from '@/constants';
import moment from 'moment';
import { computed } from 'vue';
const props = defineProps<{ project: Project }>()
const leftDays = computed(() => props.project.expire_on ? `Expire ${moment.utc(props.project.expire_on).fromNow()}` : '') 
</script>

<style scoped>
.expire {
  font-size: 0.8em;
}
</style>
