<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();

const handleLogout = () => {
  auth.logout();
  router.push("/");
};
</script>

<template>
  <aside class="sidebar-kofan shadow-sm">
    <div class="text-center mb-4 mt-2">
      <h6 class="fw-bold text-muted text-uppercase tracking-wider">Menú Kofán</h6>
      <hr class="opacity-10 mx-3">
    </div>

    <nav class="nav flex-column gap-2">
      <router-link :to="{ name: 'account-profile' }" class="nav-link-kofan">
        <i class="bi bi-person-vcard-fill me-3 fs-5 icon-kofan"></i> Mi Panel
      </router-link>
      
      <router-link :to="{ name: 'account-bookings' }" class="nav-link-kofan">
        <i class="bi bi-calendar-check-fill me-3 fs-5 icon-kofan"></i> Mis Reservas
      </router-link>
      
      <router-link :to="{ name: 'account-notifications' }" class="nav-link-kofan">
        <i class="bi bi-bell-fill me-3 fs-5 icon-kofan"></i> Todos los Avisos
      </router-link>

      <hr class="my-3 opacity-10">

      <router-link :to="{ name: 'account-settings' }" class="nav-link-kofan">
        <i class="bi bi-gear-fill me-3 fs-5 icon-kofan"></i> Configuración
      </router-link>

      <a href="#" @click.prevent="handleLogout" class="nav-link-kofan logout-link">
        <i class="bi bi-box-arrow-left me-3 fs-5 text-danger"></i> Salir
      </a>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar-kofan {
  background-color: #ffffff;
  border-radius: 20px;
  padding: 20px;
  border: 1px solid #eee;
  min-height: 50vh; /* Para que no se vea tan cortita */
}

.tracking-wider {
  letter-spacing: 1px;
}

.nav-link-kofan {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  text-decoration: none;
  color: #555;
  border-radius: 12px;
  transition: all 0.3s ease;
  font-weight: 600;
}

.nav-link-kofan:hover {
  background-color: #f0fdf4;
  color: #0f3b2a;
}

/* Estilo para la ruta activa */
/* Reemplaza el .router-link-active viejo por este */
.router-link-active {
  background-color: #eafaf1 !important; /* Verde muy clarito */
  color: #0f3b2a !important; /* Texto verde Kofán */
  font-weight: 700;
}

.logout-link:hover {
  background-color: #fff1f1;
  color: #dc3545;
}
</style>