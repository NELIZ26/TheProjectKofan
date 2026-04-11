<script setup>
import { ref, onMounted, computed } from "vue";
import apiClient from "@/api/apiClient";
import RoomHistoryCard from '@/components/RoomHistoryCard.vue'; 
import ActivityNotificationsModal from '@/components/ActivityNotificationsModal.vue';

// Variables reactivas
const stats = ref({
  ingresosMes: 0,
  reservasActivas: 0,
  huespedesHoy: 0,
  ocupacionPorcentaje: 0,
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

const normalizarAccion = (accion = "") => String(accion).toLowerCase();

const checkInsHoy = computed(
  () =>
    ultimosMovimientos.value.filter((item) =>
      /check-in|check in|llegada|ingreso/.test(normalizarAccion(item.accion)),
    ).length,
);

const checkOutsHoy = computed(
  () =>
    ultimosMovimientos.value.filter((item) =>
      /check-out|check out|salida/.test(normalizarAccion(item.accion)),
    ).length,
);

const prioridades = computed(() => [
  {
    label: "Check-ins hoy",
    value: checkInsHoy.value,
    icon: "fa-solid fa-door-open",
    tone: "sky",
  },
  {
    label: "Check-outs hoy",
    value: checkOutsHoy.value,
    icon: "fa-solid fa-key",
    tone: "apple",
  },
  {
    label: "Reservas activas",
    value: stats.value.reservasActivas,
    icon: "fa-solid fa-calendar-check",
    tone: "sand",
  },
]);

onMounted(() => {
  cargarDashboard();
});
</script>

<template>
  <div class="admin-dashboard">
    <section class="eco-card priorities-section p-4 mb-4">
      <div
        class="d-flex flex-column flex-lg-row justify-content-between align-items-start gap-3"
      >
        <div>
          <p class="brand-handmade mb-1">Bienvenida a Kofán</p>
          <h2 class="section-title h3 mb-2">Prioridades del Día</h2>
          <p class="text-muted mb-0">
            Revisa primero las llegadas, salidas y el nivel de ocupación para
            mantener una experiencia tranquila.
          </p>
        </div>

        <div class="d-flex flex-wrap gap-2">
          <router-link :to="{ name: 'admin-bookings' }" class="btn btn-kofan">
            <font-awesome-icon icon="fa-solid fa-calendar-day" class="me-2" />
            Reservas de hoy
          </router-link>
          <router-link :to="{ name: 'admin-rooms' }" class="btn btn-soft-sky">
            <font-awesome-icon icon="fa-solid fa-bed" class="me-2" /> Estado de
            habitaciones
          </router-link>
        </div>
      </div>

      <div class="row g-3 mt-1">
        <div
          v-for="item in prioridades"
          :key="item.label"
          class="col-sm-4"
        >
          <div class="priority-pill" :class="`tone-${item.tone}`">
            <div class="priority-icon">
              <font-awesome-icon :icon="item.icon" />
            </div>
            <div>
              <p class="small text-uppercase mb-1 text-muted">
                {{ item.label }}
              </p>
              <h4 class="mb-0 fw-bold text-kofan">{{ item.value }}</h4>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="eco-card h-100 p-3 card-stat">
          <div class="d-flex justify-content-between">
            <div>
              <p class="text-muted small fw-bold mb-1 text-uppercase">
                Ingresos del Mes
              </p>
              <h3 class="fw-bold mb-0 text-kofan">
                ${{ stats.ingresosMes?.toLocaleString() || 0 }}
              </h3>
            </div>
            <div class="icon-circle icon-leaf">
              <font-awesome-icon icon="fa-solid fa-hand-holding-dollar" />
            </div>
          </div>
          <div class="mt-3 small">
            <span class="trend-up fw-bold">
              <font-awesome-icon icon="fa-solid fa-arrow-up" /> 12%
            </span>
            <span class="text-muted ms-2">vs mes anterior</span>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="eco-card h-100 p-3 card-stat">
          <div class="d-flex justify-content-between">
            <div>
              <p class="text-muted small fw-bold mb-1 text-uppercase">
                Huéspedes Hoy
              </p>
              <h3 class="fw-bold mb-0 text-kofan">{{ stats.huespedesHoy }}</h3>
            </div>
            <div class="icon-circle icon-sand">
              <font-awesome-icon icon="fa-solid fa-users" />
            </div>
          </div>
          <div class="mt-3 small text-muted">En las instalaciones</div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="eco-card h-100 p-3 card-stat">
          <div class="d-flex justify-content-between">
            <div>
              <p class="text-muted small fw-bold mb-1 text-uppercase">
                Ocupación
              </p>
              <h3 class="fw-bold mb-0 text-kofan">
                {{ stats.ocupacionPorcentaje }}%
              </h3>
            </div>
            <div class="icon-circle icon-soft">
              <font-awesome-icon icon="fa-solid fa-bed" />
            </div>
          </div>
          <div class="progress mt-3" style="height: 7px">
            <div
              class="progress-bar progress-kofan"
              :style="{ width: stats.ocupacionPorcentaje + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-8">
        <div class="eco-card rounded-4 p-4 h-100">
          <p class="brand-handmade small mb-1">Preferencias de los huéspedes</p>
          <h5 class="section-title mb-4">Habitaciones más solicitadas</h5>

          <div
            v-for="(hab, index) in habitacionesPopulares"
            :key="hab.nombre"
            class="mb-4"
          >
            <div class="d-flex justify-content-between mb-1">
              <span class="fw-bold text-kofan">{{ hab.nombre }}</span>
              <span class="text-muted small">{{ hab.reservas }} reservas</span>
            </div>
            <div class="progress" style="height: 10px">
              <div
                class="progress-bar progress-kofan"
                :class="index % 2 === 0 ? 'tone-sky-bar' : 'tone-apple-bar'"
                :style="{ width: Math.min(hab.reservas * 2, 100) + '%' }"
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
.priorities-section {
  background: linear-gradient(
    135deg,
    rgba(212, 175, 55, 0.12) 0%,
    var(--k-cream) 60%,
    var(--k-apple-soft) 100%
  );
  border: 1px solid var(--k-border);
  border-radius: 20px;
}

.btn-kofan:hover {
  filter: brightness(1.03);
}

.btn-soft-sky:hover {
  box-shadow: 0 10px 20px rgba(52, 152, 219, 0.18);
}

.card-stat {
  border: 1px solid var(--k-border);
  background: var(--k-cream);
  border-radius: 18px;
  transition: transform 0.25s ease;
}

.card-stat:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
}

.priority-pill {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem;
  border-radius: 16px;
  border: 1px solid var(--k-border);
  background: rgba(255, 255, 255, 0.78);
  transition: all 0.3s ease;
}

.priority-pill:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.priority-icon,
.icon-circle {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.15rem;
}

.tone-sky .priority-icon,
.icon-sky {
  background: var(--k-sky-soft);
  color: var(--k-sky);
}

.tone-apple .priority-icon,
.icon-leaf {
  background: var(--k-apple-soft);
  color: var(--k-forest);
}

.tone-sand .priority-icon,
.icon-sand {
  background: var(--k-sand-soft);
  color: var(--k-sand);
}

.tone-forest .priority-icon,
.icon-soft {
  background: rgba(15, 59, 42, 0.1);
  color: var(--k-forest);
}

.trend-up {
  color: var(--k-forest-soft);
}

.progress {
  background: rgba(15, 59, 42, 0.06);
  border-radius: 999px;
}

.progress-kofan {
  background: linear-gradient(90deg, var(--k-forest), var(--k-apple));
}

.tone-sky-bar {
  background: linear-gradient(90deg, var(--k-sky-light), var(--k-sky));
}

.tone-apple-bar {
  background: linear-gradient(90deg, var(--k-apple), var(--k-apple-light));
}

.activity-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.activity-dot.is-ok {
  background: var(--k-apple);
}

.activity-dot.is-cancel {
  background: var(--k-danger-soft);
}

.extra-small {
  font-size: 0.75rem;
}

.rounded-4 {
  border-radius: 1.25rem;
}
</style>
