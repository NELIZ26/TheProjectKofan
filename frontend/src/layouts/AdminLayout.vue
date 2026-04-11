<script setup>
import { useAuthStore } from "@/stores/auth";
import { ref, onMounted, computed } from "vue";
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
  <div class="admin-wrapper d-flex">
    <aside class="admin-sidebar p-3 shadow-sm">
      <div class="text-center mb-4 sidebar-brand">
        <img src="@/img/Kofan.png" width="150" alt="Logo" class="brand-logo" />
        <p class="brand-handmade mt-2 mb-1 text-white">Hospitalidad Serena</p>
        <h5 class="section-title mb-0 text-white">Kofán Admin</h5>
      </div>

      <nav class="nav flex-column gap-2">
        <small class="nav-group-label">Operación diaria</small>

        <router-link :to="{ name: 'admin-dashboard' }" class="nav-link-admin">
          <font-awesome-icon icon="fa-solid fa-seedling" class="me-2" /> <span>Inicio</span>
        </router-link>
        <router-link :to="{ name: 'admin-bookings' }" class="nav-link-admin">
          <font-awesome-icon icon="fa-solid fa-calendar-check" class="me-2" /> <span>Reservas</span>
        </router-link>
        <router-link :to="{ name: 'admin-rooms' }" class="nav-link-admin">
          <font-awesome-icon icon="fa-solid fa-bed" class="me-2" /> <span>Habitaciones</span>
        </router-link>
        <router-link :to="{ name: 'admin-users' }" class="nav-link-admin">
          <font-awesome-icon icon="fa-solid fa-users" class="me-2" /> <span>Usuarios</span>
        </router-link>

        <small class="nav-group-label mt-3">Apoyo y ajustes</small>

        <router-link :to="{ name: 'admin-gallery' }" class="nav-link-admin">
          <font-awesome-icon icon="fa-solid fa-images" class="me-2" /> <span>Galería</span>
        </router-link>
        <router-link :to="{ name: 'admin-config' }" class="nav-link-admin">
          <font-awesome-icon icon="fa-solid fa-hotel" class="me-2" /> <span>Configuración</span>
        </router-link>

        <button
          @click="handleLogout"
          class="btn btn-logout-soft w-100 mt-3 shadow-sm"
        >
          <font-awesome-icon icon="fa-solid fa-right-from-bracket" class="me-2" /> <span>Salir</span>
        </button>
      </nav>
    </aside>

    <div class="main-container flex-grow-1">
      <AdminHeader />

      <main class="p-4 p-lg-4">
        <router-view></router-view>
      </main>

    </div>
  </div>
</template>

<style scoped>
/* 🟢 Quitamos el min-height: 100vh porque ahora usamos vh-100 fijo */
.admin-wrapper {
  min-height: 100vh;
  background-color: var(--k-cream);
}

.admin-sidebar {
  width: 272px;
  min-height: 100vh;
  position: sticky;
  top: 0;
  z-index: 1000;
  background: linear-gradient(180deg, var(--k-forest) 0%, var(--k-forest-soft) 100%);
  border-right: 1px solid rgba(255, 252, 248, 0.08);
}

.brand-logo {
  filter: drop-shadow(0 8px 18px rgba(15, 59, 42, 0.18));
}

/* 🟢 Asegura que el contenido no se pegue al borde */
.main-container {
  display: flex;
  flex-direction: column;
  background: var(--k-offwhite);
}

.nav {
  color: var(--k-cream);
}

.nav-group-label {
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255, 252, 248, 0.7);
  padding: 0 0.45rem;
}

/* Tus estilos de Nav-Links se mantienen iguales... */
.nav-link-admin {
  color: rgba(255, 252, 248, 0.92);
  text-decoration: none;
  padding: 12px 15px;
  border-radius: 14px;
  transition: all 0.3s ease;
  font-weight: 500;
  border: 1px solid transparent;
}

.nav-link-admin:hover {
  background: rgba(255, 255, 255, 0.12);
  color: var(--k-cream);
  border-color: rgba(255, 255, 255, 0.18);
  box-shadow: 0 10px 22px rgba(15, 59, 42, 0.12);
  transform: translateX(2px);
}

.router-link-active {
  background: var(--k-apple-soft) !important;
  color: var(--k-forest) !important;
  border-color: rgba(139, 207, 91, 0.55);
  box-shadow: 0 8px 20px rgba(139, 207, 91, 0.18);
}

.page-intro {
  padding-left: 0.25rem;
}

.btn-logout-soft {
  background-color: var(--k-danger-soft);
  color: var(--k-danger);
  border: 1px solid var(--k-danger-border);
  font-family: 'Handlee', cursive;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-logout-soft:hover {
  background-color: var(--k-danger-strong);
  color: var(--k-offwhite);
  border-color: var(--k-danger);
  box-shadow: 0 4px 12px rgba(224, 49, 49, 0.25) !important;
}

.btn-logout-soft:hover :deep(svg) {
  transform: translateX(3px);
  transition: transform 0.2s ease;
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 88px;
  }

  .admin-sidebar span,
  .admin-sidebar h5,
  .admin-sidebar .brand-handmade,
  .nav-group-label {
    display: none;
  }

  .nav-link-admin {
    text-align: center;
    padding: 15px;
  }

  .nav-link-admin :deep(svg) {
    margin: 0 !important;
    font-size: 1.2rem;
  }
}
</style>
