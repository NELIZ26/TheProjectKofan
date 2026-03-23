<script setup>
import Navbar from "@/components/Navbar.vue";
import Footer from "@/components/Footer.vue";
import ReservaModal from "@/components/ReservaModal.vue";
</script>

<template>
  <main id="page">
    <Navbar v-if="$route.name !== 'not-found' && !$route.path.startsWith('/admin') && !$route.meta.hideNavbar" />
    
    <div id="content">
      <router-view />
    </div>
    
    <Footer v-if="$route.name !== 'not-found' && !$route.path.startsWith('/admin') && !$route.meta.hideNavbar" />
    
    <ReservaModal />
  </main>
</template>

<style>

</style>
