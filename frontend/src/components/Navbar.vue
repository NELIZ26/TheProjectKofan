<script setup>
import { useRouter, useRoute } from "vue-router";
import { computed, ref, onMounted, onUnmounted, watch } from "vue";
import { useAuthStore } from "@/stores/auth";
import { Collapse } from "bootstrap";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const isScrolled = ref(false);
const handleScroll = () => { isScrolled.value = window.scrollY > 50; };

let bsCollapse = null;
onMounted(() => {
  window.addEventListener("scroll", handleScroll);
  const menuElement = document.getElementById("navbarKofan");
  if (menuElement) bsCollapse = new Collapse(menuElement, { toggle: false });
});

onUnmounted(() => { window.removeEventListener("scroll", handleScroll); });

watch(() => route.path, () => { if (bsCollapse) bsCollapse.hide(); });

const logout = () => {
  auth.logout();
  router.push({ name: 'landing-portal' });
};

const navbarSolid = computed(() => {
  if (isScrolled.value) return true;
  const nombresSolid = ["login", "register", "account-profile", "rooms", "account-bookings", "account-notifications", "account-booking-detail"];
  return nombresSolid.includes(route.name) || route.path.startsWith("/app") || route.path.startsWith("/admin");
});
</script>

<template>
  <header
    class="navbar navbar-expand-lg fixed-top transition-navbar"
    :class="navbarSolid ? 'navbar-dark bg-kofan shadow-sm' : 'navbar-dark bg-transparent'"
  >
    <div class="container-fluid px-lg-5">
      <router-link :to="{ name: 'landing-portal' }" class="navbar-brand">
        <img src="../img/Kofan.png" width="80" alt="Logo Kofán" />
      </router-link>

      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarKofan">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarKofan">
        <ul class="navbar-nav mx-auto mb-2 mb-lg-0 fw-medium">
          <li class="nav-item">
            <router-link :to="{ name: 'hospedaje-home' }" class="nav-link" exact-active-class="active-link">Inicio</router-link>
          </li>
          <li class="nav-item">
            <router-link :to="{ name: 'about' }" class="nav-link" active-class="active-link">Nosotros</router-link>
          </li>
          <li class="nav-item">
            <router-link :to="{ name: 'rooms' }" class="nav-link" active-class="active-link">Servicios</router-link>
          </li>
          <li class="nav-item">
            <router-link :to="{ name: 'gallery' }" class="nav-link" active-class="active-link">Galería</router-link>
          </li>
        </ul>

        <div class="d-lg-flex align-items-center gap-3">
          <button class="btn btn-success rounded-pill px-4 d-none d-xl-block fw-bold" @click="router.push({ name: 'contact' })">
            Contáctanos
          </button>

          <div v-if="!auth.isLogged" class="d-flex align-items-center gap-2">
            <router-link :to="{ name: 'login' }" class="btn-ingresar-kofan">
              Ingresar
            </router-link>
            <router-link :to="{ name: 'register' }" class="btn btn-success btn-sm px-3 rounded-pill">
              Registrarse
            </router-link>
          </div>

          <div v-else class="dropdown">
            <button class="btn btn-success dropdown-toggle d-flex align-items-center gap-2 rounded-pill px-3" data-bs-toggle="dropdown">
               <font-awesome-icon :icon="['fas', 'user-circle']" />
               <span>{{ auth.user?.full_name }}</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end shadow border-0 mt-2">
              <li>
                <router-link class="dropdown-item" :to="{ name: 'account-profile' }">
                  <font-awesome-icon :icon="['fas', 'id-card']" class="me-2" /> Mi Perfil
                </router-link>
              </li>
              <li v-if="auth.user?.role === 'admin'">
                <router-link class="dropdown-item text-success fw-bold" :to="{ name: 'admin-dashboard' }">
                  <font-awesome-icon :icon="['fas', 'chart-line']" class="me-2" /> Panel Admin
                </router-link>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li><a class="dropdown-item text-danger" href="#" @click.prevent="logout">
                <font-awesome-icon :icon="['fas', 'sign-out-alt']" class="me-2" /> Cerrar Sesión
              </a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.transition-navbar { transition: all 0.4s ease-in-out; padding: 1rem 0; }
.bg-kofan { background-color: #0f3b2a !important; padding: 0.5rem 0; }

.nav-link {
  color: white !important;
  margin: 0 10px;
  position: relative;
  text-decoration: none;
}

.nav-link::after {
  content: ''; position: absolute; width: 0; height: 2px;
  bottom: -2px; left: 50%; background: #2ecc71;
  transition: all 0.3s ease; transform: translateX(-50%);
}

.nav-link:hover::after { width: 60%; }
.active-link::after { width: 80% !important; }
.active-link { color: #2ecc71 !important; }

.btn-ingresar-kofan {
  color: white !important;
  text-decoration: none;
  font-weight: 500;
  padding: 5px 15px;
  border: 1px solid rgba(255,255,255,0.4);
  border-radius: 8px;
  transition: all 0.3s;
}

.btn-ingresar-kofan:hover {
  border-color: #2ecc71;
  background: rgba(255, 255, 255, 0.1);
}
</style>