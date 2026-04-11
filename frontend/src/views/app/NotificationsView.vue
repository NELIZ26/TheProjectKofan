<script setup>
import { ref, onMounted } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";

// Empezamos con un array vacío
const avisos = ref([]);

// 🟢 Traemos los datos reales al cargar la página
const cargarAvisos = async () => {
  try {
    const response = await apiClient.get('/api/notificaciones/mis-avisos');
    avisos.value = response.data;
  } catch (error) {
    console.error("Error cargando avisos:", error);
  }
};

onMounted(() => {
  cargarAvisos();
});

// 🟢 Enviamos la orden de leer al backend
const marcarTodosLeidos = async () => {
  try {
    await apiClient.patch('/api/notificaciones/read-all');
    
    // Cambiamos visualmente el estado a leídas
    avisos.value.forEach(a => a.leida = true);

    // 🟢 EL MEGÁFONO: Le avisamos al menú lateral que actualice la campanita YA
    window.dispatchEvent(new Event('notificaciones-leidas'));

    Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 2000,
      timerProgressBar: true,
    }).fire({
      icon: 'success',
      title: 'Avisos marcados como leídos'
    });
  } catch (error) {
    console.error("Error al marcar leídos:", error);
  }
};

const resolverIconoAviso = (icono) => {
  const valor = String(icono || '').toLowerCase();

  if (valor.includes('check')) return 'fa-solid fa-circle-check';
  if (valor.includes('info')) return 'fa-solid fa-circle-info';
  if (valor.includes('house') || valor.includes('door')) return 'fa-solid fa-house-chimney';
  if (valor.includes('x') || valor.includes('ban') || valor.includes('cancel')) return 'fa-solid fa-ban';
  if (valor.includes('bell')) return 'fa-solid fa-bell';

  return 'fa-solid fa-bell';
};
</script>

<template>
  <div class="container-fluid py-2">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="fw-bold text-dark mb-1">Centro de Avisos</h4>
        <p class="text-muted mb-0 small">Mantente al tanto de tus reservas y promociones exclusivas.</p>
      </div>
      <button @click="marcarTodosLeidos" class="btn btn-outline-dark rounded-pill px-4 shadow-sm fw-medium">
        <font-awesome-icon icon="fa-solid fa-circle-check" class="me-2" /> Marcar como leídos
      </button>
    </div>

    <div class="d-flex flex-column gap-3">
      
      <div v-if="avisos.length === 0" class="text-center py-5">
        <font-awesome-icon icon="fa-solid fa-bell-slash" class="display-4 mb-3 d-block text-light" />
        <h6 class="text-muted fw-bold">No tienes avisos recientes</h6>
        <p class="text-muted small">Aquí aparecerán las actualizaciones de tus reservas.</p>
      </div>

      <div 
        v-for="aviso in avisos" 
        :key="aviso.id" 
        class="card border-0 shadow-sm rounded-4 overflow-hidden aviso-card"
        :class="`border-start border-4 border-${aviso.colorTheme}`"
      >
        <div class="card-body p-3 p-md-4 d-flex align-items-start gap-3">
          
          <div 
            class="rounded-3 d-flex align-items-center justify-content-center flex-shrink-0" 
            :class="`bg-${aviso.colorTheme} bg-opacity-10 text-${aviso.colorTheme}`" 
            style="width: 50px; height: 50px;"
          >
            <font-awesome-icon :icon="resolverIconoAviso(aviso.icono)" class="fs-4" />
          </div>
          
          <div class="flex-grow-1">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <h6 class="fw-bold mb-0 text-dark">{{ aviso.titulo }}</h6>
              <small class="text-muted"><font-awesome-icon icon="fa-solid fa-clock" class="me-1" /> {{ aviso.fecha }}</small>
            </div>
            <p class="mb-0 text-secondary small">{{ aviso.mensaje }}</p>
          </div>
          
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.aviso-card {
  transition: transform 0.2s ease, background-color 0.2s ease;
  cursor: default;
}

.aviso-card:hover {
  transform: translateX(6px);
  background-color: #f8f9fa !important;
}
</style>