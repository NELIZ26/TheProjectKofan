<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import Navbar from "@/components/Navbar.vue";
import Footer from "@/components/Footer.vue";
import ReservaModal from "@/components/ReservaModal.vue";

const route = useRoute();
const showPublicChrome = computed(() => !route.meta.hideNav);
</script>

<template>
  <main id="page">
    <Navbar v-if="showPublicChrome" />
    <router-view />
    <ReservaModal />
    <Footer v-if="showPublicChrome" />
  </main>
</template>

<style>
/* Estilos globales básicos */
</style>