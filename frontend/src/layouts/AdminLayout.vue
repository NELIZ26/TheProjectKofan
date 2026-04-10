<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted } from "vue"
import AdminHeader from "@/views/admin/AdminHeader.vue";
import { useRouter } from "vue-router";
import { getUserProfile } from "@/services/authServices";

const auth = useAuthStore();
const router = useRouter();

const user = ref();
const errorMessage = ref("");
const isLoading = ref(false);
const sidebarCollapsed = ref(false);

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

const loadProfile = async () => {
  try {
    const profile = await getUserProfile();
    user.value = profile;
  } catch (error) {
    errorMessage.value = "Sesión expirada o inválida";
    auth.logout();
    router.push("/auth/login");
  } finally {
    isLoading.value = false;
  }
};

// 🟢 FUNCIÓN CORREGIDA
const handleLogout = () => {
  console.log("Cerrando sesión..."); // Para verificar en consola (F12) que el botón sí se presiona
  auth.logout();
  
  // 🟢 Lo enviamos a la ruta segura de login en lugar de "hospedaje-home"
  router.push("/auth/login"); 
};

onMounted(() => {
  loadProfile();
});
</script>

<template>
  <div class="admin-wrapper d-flex vh-100 overflow-hidden">
    
    <aside class="admin-sidebar bg-dark text-white p-3 shadow flex-shrink-0">
      <div class="text-center mb-4">
        <img src="@/img/Kofan.png" width="100" alt="Logo" class="filter-white" />
        <h5 class="mt-2 fw-bold text-success">Kofán Admin</h5>
      </div>

      <nav class="nav flex-column gap-2">
        <router-link :to="{ name: 'admin-dashboard' }" class="nav-link-admin">
          <i class="fa fa-chart-line me-2"></i> <span>Dashboard</span>
        </router-link>
        <router-link :to="{ name: 'admin-rooms' }" class="nav-link-admin">
          <i class="fa fa-bed me-2"></i> <span>Habitaciones</span>
        </router-link>
        <router-link :to="{ name: 'admin-users' }" class="nav-link-admin">
          <i class="fa fa-users me-2"></i> <span>Usuarios</span>
        </router-link>
        <router-link :to="{ name: 'admin-bookings' }" class="nav-link-admin">
          <i class="fa fa-calendar-check me-2"></i> <span>Reservas</span>
        </router-link>
        <router-link :to="{ name: 'admin-gallery' }" class="nav-link-admin">
          <i class="fa fa-images me-2"></i> <span>Galería</span>
        </router-link>
        
        <router-link :to="{ name: 'admin-config' }" class="nav-link-admin">
          <i class="fa fa-cog me-2"></i> <span>Configuración</span>
        </router-link>
        
        <hr class="border-secondary opacity-25">
        
        <button @click="handleLogout" class="btn btn-outline-danger w-100 mt-2 border-0 shadow-sm">
          <i class="fa fa-sign-out-alt me-2"></i> <span>Salir</span>
        </button>
      </nav>
    </aside>

    <div class="main-container flex-grow-1 d-flex flex-column min-w-0 bg-light">
      
      <header class="bg-white shadow-sm flex-shrink-0 z-1 w-100">
          <AdminHeader />
          <div class="px-4 py-2 border-top d-flex justify-content-between align-items-center bg-white">
            <h3 class="text-dark fw-bold text-capitalize mb-0" style="font-size: 1.5rem;">
              {{ $route.name?.replace('admin-', '') }}
            </h3>
            </div>
            </header>
      
      <main class="p-4 overflow-auto flex-grow-1">
        <router-view></router-view>
      </main>

    </div>
  </div>
</template>

<style scoped>
/* 🟢 Quitamos el min-height: 100vh porque ahora usamos vh-100 fijo */
.admin-wrapper {
  background-color: #f8f9fa;
}

.admin-sidebar {
  width: 260px;
  /* 🟢 Quitamos sticky porque el contenedor padre ya no scrollea */
  overflow-y: auto; 
}

/* 🟢 Asegura que el contenido no se pegue al borde */
.main-container {
  height: 100%;
}

.z-1 {
  z-index: 10;
}

/* Tus estilos de Nav-Links se mantienen iguales... */
.nav-link-admin {
  color: #adb5bd;
  text-decoration: none;
  padding: 12px 15px;
  border-radius: 10px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-link-admin:hover {
  background: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
}

.router-link-active {
  background: #0f3b2a !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(15, 59, 42, 0.3);
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 85px;
  }
  .admin-sidebar span, .admin-sidebar h5 {
    display: none;
  }
}

.admin-wrapper {
  height: 100vh; /* Forzamos el alto de la ventana */
}

/* Aseguramos que el header no se mueva ni se oculte */
header {
  position: relative;
  background-color: #fff;
}

/* Ajuste para el scroll del main */
main {
  background-color: #f8f9fa; /* Fondo gris claro para que resalten las tarjetas blancas */
  scrollbar-width: thin; /* Para que la barra de scroll sea elegante en Firefox */
  scrollbar-color: #2ecc71 #f8f9fa;
}
</style>