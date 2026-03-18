<script setup>
import Navbar from "@/components/Navbar.vue";
import Footer from "@/components/Footer.vue";
import Sidebar from "@/views/app/SidebarView.vue";
import { useRoute } from "vue-router";
import { ref, watch } from "vue";

const route = useRoute();
const routeChange = ref(0);

// Fuerza una re-evaluación mínima cuando cambia la ruta
watch(() => route.path, () => {
  routeChange.value++;
});
</script>

<template>
  <div class="app-layout">

    <div class="container-fluid mt-5 pt-5">
      <div class="row">
        <aside class="col-12 col-lg-3 bd-sidebar mb-4">
          <Sidebar />
        </aside>

        <main class="col-12 col-lg-9">
          <div class="p-4 shadow-sm bg-white rounded-4 min-vh-100">
            <router-view />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  background-color: #f8f9fa;
  min-height: 100vh; /* Corregido: propiedad completa */
}

@media (min-width: 992px) {
  .bd-sidebar {
    position: sticky;
    top: 100px; 
    /* Ajustamos el alto para que no choque con el footer */
    height: calc(100vh - 120px);
    overflow-y: auto; 
  }
}
</style>