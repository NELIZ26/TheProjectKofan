<script setup>
import { onMounted } from 'vue';
import Navbar from "@/components/Navbar.vue";
import Footer from "@/components/Footer.vue";
import { useConfigStore } from '@/stores/config';

// Inicializamos el store
const configStore = useConfigStore();

// Pedimos la configuración al cargar la zona pública
onMounted(() => {
  configStore.fetchSiteConfig();
});
</script>

<template>
  <div class="public-layout d-flex flex-column min-vh-100">
    <Navbar />
    
    <div id="content" class="flex-grow-1">
      <router-view /> 
    </div>
    
    <Footer />
  </div>
</template>