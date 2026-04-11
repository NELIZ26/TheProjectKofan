<script setup>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import Swal from "sweetalert2";

const auth = useAuthStore();
const router = useRouter();

const firstName = computed(
  () => auth.user?.full_name?.trim()?.split(" ")?.[0] || "Anfitrión",
);

const getBrandColor = (token, fallback) =>
  typeof window !== "undefined"
    ? getComputedStyle(document.documentElement).getPropertyValue(token).trim() || fallback
    : fallback;

const COLOR_APPLE = getBrandColor("--k-apple", "#8BCF5B");
const COLOR_FOREST = getBrandColor("--k-forest", "#0f3b2a");

const handleLogout = () => {
  Swal.fire({
    title: "¿Deseas cerrar tu jornada por ahora?",
    text: "Podrás volver a entrar cuando lo necesites.",
    icon: "question",
    showCancelButton: true,
    confirmButtonColor: COLOR_APPLE,
    cancelButtonColor: COLOR_FOREST,
    confirmButtonText: "Sí, salir por ahora",
    cancelButtonText: "Seguir aquí",
  }).then((result) => {
    if (result.isConfirmed) {
      auth.logout();
      router.push({ name: "hospedaje-home" });
    }
  });
};
</script>

<template>
  <header
    class="admin-header d-flex align-items-center justify-content-between px-4"
  >
    <div class="header-left d-flex align-items-center gap-3">
      <button class="btn btn-soft-sky d-md-none me-1">
        <font-awesome-icon icon="fa-solid fa-filter" />
      </button>
    </div>
    <div class="header-right d-flex align-items-center gap-3">
      <div class="user-profile d-none d-sm-flex align-items-center">
        <div class="user-info text-end me-2">
          <p class="mb-0 fw-bold lh-1 text-kofan text-white">{{ auth.user?.full_name }}</p>
          <small class=" text-white">Equipo Kofán</small>
        </div>
        <div class="avatar-circle">
          {{ auth.user?.full_name?.charAt(0) }}
        </div>
      </div>

      <div class="vertical-divider"></div>

      <button
        @click="handleLogout"
        class="btn btn-logout-soft-sm btn-sm px-3 shadow-sm"
      >
        <font-awesome-icon icon="fa-solid fa-right-from-bracket" class="me-1" /> Salir
      </button>
    </div>
  </header>
</template>

<style scoped>
.admin-header {
  min-height: 78px;
  width: 100%;
  background: linear-gradient(135deg, var(--k-forest) 0%, var(--k-apple) 62%, var(--k-forest) 100%);
  backdrop-filter: blur(4px);
}

.avatar-circle {
  width: 40px;
  height: 40px;
  background: var(--k-forest);
  color: var(--k-offwhite);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  box-shadow: 0 8px 18px rgba(139, 207, 91, 0.24);
}

.vertical-divider {
  width: 1px;
  height: 30px;
  background-color: rgba(255, 252, 248, 0.4);
  margin: 0 4px;
}

.lh-1 {
  line-height: 1;
}

.btn-logout-soft-sm {
  background-color: var(--k-danger-soft);
  color: var(--k-danger);
  border: 1px solid var(--k-danger-border);
  font-family: 'Handlee', cursive;
  font-weight: 600;
  transition: all 0.25s ease;
  display: inline-flex;
  align-items: center;
}

.btn-logout-soft-sm:hover {
  background-color: var(--k-danger-strong);
  color: var(--k-offwhite);
  border-color: var(--k-danger);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(250, 82, 82, 0.2) !important;
}

.btn-logout-soft-sm:hover :deep(svg) {
  transform: scale(1.1);
  transition: transform 0.2s ease;
}
</style>
