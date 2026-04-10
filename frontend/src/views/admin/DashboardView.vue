<script setup>
import { ref, onMounted } from 'vue';
import apiClient from "@/api/apiClient";
import RoomHistoryCard from '@/components/RoomHistoryCard.vue'; 
import ActivityNotificationsModal from '@/components/ActivityNotificationsModal.vue';

// Variables reactivas
const stats = ref({
  ingresosMes: 0,
  reservasActivas: 0,
  huespedesHoy: 0,
  ocupacionPorcentaje: 0
});

const modalAvisosVisible = ref(false); // Controla el nuevo NotificationModal
const habitacionesPopulares = ref([]);
const ultimosMovimientos = ref([]);

// Función para cargar los datos del dashboard
const cargarDashboard = async () => {
  try {
    const response = await apiClient.get('/dashboard'); 
    
    // Validaciones de seguridad con optional chaining
    stats.value = response.data?.stats || { ingresosMes: 0, reservasActivas: 0, huespedesHoy: 0, ocupacionPorcentaje: 0 };
    habitacionesPopulares.value = response.data?.habitacionesPopulares || [];
    ultimosMovimientos.value = response.data?.ultimosMovimientos || [];
    
  } catch (error) {
    console.error("Error trayendo los datos del dashboard:", error);
  }
};

onMounted(() => {
  cargarDashboard();
});
</script>

<template>
  <div class="admin-dashboard">
    <div class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100 p-3 card-stat">
          <div class="d-flex justify-content-between">
            <div>
              <p class="text-muted small fw-bold mb-1 text-uppercase">Ingresos del Mes</p>
              <h3 class="fw-bold mb-0">${{ stats.ingresosMes.toLocaleString() }}</h3>
            </div>
            <div class="icon-circle bg-success-subtle text-success">
              <font-awesome-icon icon="fa-solid fa-hand-holding-dollar" />
            </div>
          </div>
          <div class="mt-3 small">
            <span class="text-success fw-bold"><font-awesome-icon icon="fa-solid fa-arrow-up" /> 12%</span>
            <span class="text-muted ms-2">vs mes anterior</span>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100 p-3 card-stat">
          <div class="d-flex justify-content-between">
            <div>
              <p class="text-muted small fw-bold mb-1 text-uppercase">Reservas Activas</p>
              <h3 class="fw-bold mb-0">{{ stats.reservasActivas }}</h3>
            </div>
            <div class="icon-circle bg-primary-subtle text-primary">
              <font-awesome-icon icon="fa-solid fa-calendar-check" />
            </div>
          </div>
          <div class="mt-3 small text-muted">Próximos 7 días</div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100 p-3 card-stat">
          <div class="d-flex justify-content-between">
            <div>
              <p class="text-muted small fw-bold mb-1 text-uppercase">Huéspedes Hoy</p>
              <h3 class="fw-bold mb-0">{{ stats.huespedesHoy }}</h3>
            </div>
            <div class="icon-circle bg-warning-subtle text-warning">
              <font-awesome-icon icon="fa-solid fa-users" />
            </div>
          </div>
          <div class="mt-3 small text-muted">En las instalaciones</div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 shadow-sm h-100 p-3 card-stat text-white bg-dark">
          <div class="d-flex justify-content-between">
            <div>
              <p class="text-light opacity-75 small fw-bold mb-1 text-uppercase">Ocupación</p>
              <h3 class="fw-bold mb-0">{{ stats.ocupacionPorcentaje }}%</h3>
            </div>
            <div class="icon-circle bg-white text-dark">
              <font-awesome-icon icon="fa-solid fa-bed" />
            </div>
          </div>
          <div class="progress mt-3" style="height: 6px;">
            <div class="progress-bar bg-success" :style="{ width: stats.ocupacionPorcentaje + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-12 col-lg-8">
        <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
          <h5 class="fw-bold mb-4">Habitaciones más solicitadas</h5>
          
          <div v-for="hab in habitacionesPopulares" :key="hab.nombre" class="mb-4">
            <div class="d-flex justify-content-between mb-1">
              <span class="fw-bold">{{ hab.nombre }}</span>
              <span class="text-muted small">{{ hab.reservas }} reservas</span>
            </div>
            <div class="progress" style="height: 10px;">
              <div 
                :class="['progress-bar', 'bg-' + hab.color]" 
                :style="{ width: (hab.reservas * 2) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-lg-4">
        <div class="card border-0 shadow-sm rounded-4 p-4 mb-4">
          <h5 class="fw-bold mb-4">Actividad de Reservas</h5>
          
          <div v-for="item in (ultimosMovimientos || []).slice(0, 3)" :key="item.id" 
               class="d-flex mb-3 align-items-center p-3 bg-white border shadow-sm rounded-3 notification-item">
            <div class="activity-dot flex-shrink-0 me-3" :class="item.accion === 'Cancelación' ? 'bg-danger' : 'bg-success'"></div>
            <div class="flex-grow-1 min-w-0">
              <h6 class="mb-0 fw-bold small text-truncate">{{ item.usuario }}</h6>
              <p class="mb-0 text-muted extra-small text-truncate">{{ item.accion }} - {{ item.fecha }}</p>
            </div>
            <div class="fw-bold small text-nowrap ms-2">{{ item.monto.replace(/\.0$/, '') }}</div>
          </div>

          <button @click="modalAvisosVisible = true" class="btn btn-light btn-sm w-100 mt-2 fw-bold text-muted rounded-3">
            Ver todas las reservas y avisos
          </button>
        </div>

        <RoomHistoryCard />
      </div>
    </div>
    
    <ActivityNotificationsModal :show="modalAvisosVisible" @close="modalAvisosVisible = false" />

  </div>
</template>

<style scoped>
.card-stat {
  border-radius: 18px;
  transition: transform 0.3s ease;
}

.card-stat:hover {
  transform: translateY(-5px);
}

.icon-circle {
  width: 45px;
  height: 45px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.activity-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.extra-small {
  font-size: 0.75rem;
}

.rounded-4 {
  border-radius: 1.25rem;
}

.bg-success-subtle { background-color: #d1e7dd; }
.bg-primary-subtle { background-color: #cfe2ff; }
.bg-warning-subtle { background-color: #fff3cd; }
</style>