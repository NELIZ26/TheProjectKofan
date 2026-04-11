<script setup>
import { onMounted } from 'vue';
import { useConfigStore } from '@/stores/config';

const configStore = useConfigStore();

onMounted(() => {
  configStore.fetchSiteConfig();
});
</script>

<template>
  <div class="public-layout d-flex flex-column min-vh-100">
    <div id="content" class="flex-grow-1">
      <router-view /> 
    </div>
  </div>
</template>