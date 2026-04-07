<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useReservaStore } from "@/stores/reserva";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";

const auth = useAuthStore();
const resStore = useReservaStore();

// --- 1. ESTADO REACTIVO ---
const checkInDate = ref("");
const checkOutDate = ref("");
const filtroEstado = ref("todas"); // 🟢 Ahora usamos minúsculas
const isLoading = ref(true);

const reservas = ref([]);
const reservasFiltradas = ref([]);

// 🟢 TABS DINÁMICOS (Sincronizados con el backend)
const tabs = [
  { id: "todas", label: "Todas" },
  { id: "pendiente", label: "Pendientes" },
  { id: "confirmada", label: "Confirmadas" },
  { id: "ocupada", label: "En Curso" }
];

// --- 2. PROPIEDADES COMPUTADAS ---
const listaVisual = computed(() => {
  if (filtroEstado.value === "todas") return reservasFiltradas.value;
  return reservasFiltradas.value.filter((r) => r.estado === filtroEstado.value);
});

// --- 3. CONEXIÓN A LA API (BACKEND) ---
const cargarMisReservas = async () => {
  isLoading.value = true;
  try {
    const response = await apiClient.get("/api/reservas/mis-reservas");
    
    // Mapeamos los datos de la Base de Datos para que encajen con nuestra tabla visual
    reservas.value = response.data.map(res => ({
      id: res._id || res.id,
      detalle: res.habitacion_nombre || res.room_name || "Hospedaje Kofán", 
      fechaReserva: formatFecha(res.fecha_creacion || res.created_at || new Date().toISOString().split('T')[0]),
      checkIn: res.fecha_entrada || res.check_in_date,
      checkOut: res.fecha_salida || res.check_out_date,
      // 🟢 Ahora lo guardamos en minúsculas para que coincida exacto con los Tabs
      estado: res.estado ? res.estado.toLowerCase() : "pendiente"
    }));

    // Actualizamos la lista filtrada con los datos frescos
    reservasFiltradas.value = [...reservas.value];

  } catch (error) {
    console.error("Error al cargar las reservas:", error);
    Swal.fire({
      toast: true, position: 'top-end', showConfirmButton: false, timer: 3000,
      icon: 'error', title: 'No se pudieron cargar tus reservas'
    });
  } finally {
    isLoading.value = false;
  }
};

// Se ejecuta automáticamente al abrir la vista
onMounted(() => { 
  cargarMisReservas(); 
});

// --- 4. MÉTODOS DE INTERFAZ Y FILTROS ---
const filtrarLista = () => {
  if (!checkInDate.value || !checkOutDate.value) {
    Swal.fire({ icon: "warning", title: "Fechas incompletas", text: "Selecciona un rango de inicio y fin.", confirmButtonColor: "#212529" });
    return;
  }
  const inicio = new Date(checkInDate.value);
  const fin = new Date(checkOutDate.value);
  
  reservasFiltradas.value = reservas.value.filter((r) => {
    const fechaIn = new Date(r.checkIn);
    return fechaIn >= inicio && fechaIn <= fin;
  });
};

const limpiarFiltros = () => {
  if (!checkInDate.value && !checkOutDate.value && filtroEstado.value === "todas") return;
  checkInDate.value = "";
  checkOutDate.value = "";
  filtroEstado.value = "todas";
  reservasFiltradas.value = [...reservas.value];
  Swal.mixin({ toast: true, position: "top-end", showConfirmButton: false, timer: 2000 }).fire({ icon: "success", title: "Filtros eliminados" });
};

const formatFecha = (fechaISO) => {
  if (!fechaISO) return "";
  const [year, month, day] = fechaISO.split("-");
  return `${day}/${month}/${year}`;
};

// --- 5. DISEÑO DE INSIGNIAS KOFÁN ---
// 🟢 Función para mostrar un nombre amigable al cliente (En Curso en vez de Ocupada)
const getNombreEstadoVisual = (estado) => {
  if (estado === 'ocupada') return 'En Curso';
  return estado;
};

const getBadgeClass = (estado) => {
  if (estado === 'confirmada') return 'bg-success bg-opacity-10 text-success border border-success';
  if (estado === 'pendiente') return 'bg-warning bg-opacity-10 text-warning border border-warning-subtle';
  if (estado === 'ocupada') return 'bg-info bg-opacity-10 text-info border border-info';
  if (estado === 'finalizada') return 'bg-secondary bg-opacity-10 text-secondary border border-secondary-subtle';
  if (estado === 'cancelada') return 'bg-danger bg-opacity-10 text-danger border border-danger';
  return 'bg-light text-dark border border-secondary';
};

const getBadgeIcon = (estado) => {
  if (estado === 'confirmada') return 'bi bi-check-circle-fill';
  if (estado === 'pendiente') return 'bi bi-clock-fill';
  if (estado === 'ocupada') return 'bi bi-house-door-fill'; // 🟢 Icono para check-in
  if (estado === 'finalizada') return 'bi bi-check2-all';   // 🟢 Icono para check-out
  if (estado === 'cancelada') return 'bi bi-x-circle-fill';
  return 'bi bi-info-circle-fill';
};
</script>

<template>
  <div class="container-fluid py-2">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="fw-bold text-dark mb-1">Mis Reservas</h4>
        <p class="text-muted mb-0 small">
          Titular: <span class="fw-bold text-dark">{{ auth.user?.full_name || "Huésped" }}</span>
        </p>
      </div>
      <button @click="resStore.openModal" class="btn btn-dark rounded-pill px-4 shadow-sm fw-medium">
        <i class="bi bi-calendar-plus-fill me-2"></i> Nueva Reserva
      </button>
    </div>

    <div class="card border-0 shadow-sm rounded-4 p-3 mb-4 bg-white d-inline-block w-100">
      <div class="d-flex flex-wrap gap-3 align-items-end">
        
        <div>
          <label class="form-label small fw-bold text-secondary mb-1">Desde</label>
          <input type="date" v-model="checkInDate" class="form-control rounded-3 shadow-none border-light-subtle bg-light" style="min-width: 160px;" />
        </div>
        
        <div>
          <label class="form-label small fw-bold text-secondary mb-1">Hasta</label>
          <input type="date" v-model="checkOutDate" class="form-control rounded-3 shadow-none border-light-subtle bg-light" style="min-width: 160px;" />
        </div>
        
        <div class="d-flex gap-2 ms-auto ms-md-0">
          <button 
            @click="filtrarLista" 
            class="btn bg-transparent border-0 text-dark rounded-circle d-inline-flex align-items-center justify-content-center transition-all" 
            style="width: 42px; height: 42px; box-shadow: 0 2px 5px rgba(0,0,0,0.03);" 
            title="Buscar reservas"
          >
            <i class="bi bi-search fs-5 fw-bold"></i>
          </button>

          <button 
            v-if="checkInDate || checkOutDate" 
            @click="limpiarFiltros" 
            class="btn btn-light border text-danger rounded-circle shadow-sm d-inline-flex align-items-center justify-content-center transition-all" 
            style="width: 42px; height: 42px;" 
            title="Limpiar fechas"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

      </div>
    </div>

    <div class="bg-light p-1 rounded-pill d-flex border shadow-sm mb-4 overflow-auto">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        class="btn rounded-pill px-4 fw-bold border-0 flex-grow-1 transition-all text-nowrap" 
        :class="filtroEstado === tab.id ? 'btn-dark text-white shadow' : 'text-muted'" 
        @click="filtroEstado = tab.id"
      >
        {{ tab.label }} <span v-if="tab.id === 'todas'" class="ms-1">({{ reservasFiltradas.length }})</span>
      </button>
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th class="py-3 px-4 text-muted small fw-bold">DETALLE DEL HOSPEDAJE</th>
              <th class="py-3 text-muted small fw-bold text-center">REGISTRO</th>
              <th class="py-3 text-center text-muted small fw-bold">ESTANCIA (IN - OUT)</th>
              <th class="py-3 text-center text-muted small fw-bold">ESTADO</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="reserva in listaVisual" :key="reserva.id" class="cursor-pointer">
              <td class="px-4 py-3">
                <router-link :to="{ name: 'account-booking-detail', params: { id: reserva.id } }" class="text-decoration-none d-flex align-items-center">
                  <div class="bg-success bg-opacity-10 text-success rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                    <i class="bi bi-house-door-fill fs-5"></i>
                  </div>
                  <div>
                    <div class="fw-bold text-dark">{{ reserva.detalle }}</div>
                    <small class="text-muted"><i class="bi bi-people-fill me-1"></i> Huéspedes Adultos</small>
                  </div>
                </router-link>
              </td>
              <td class="text-muted small text-center">{{ reserva.fechaReserva }}</td>
              <td class="text-center">
                <div class="small text-muted mb-1"><i class="bi bi-box-arrow-in-right text-success me-1"></i> In: {{ formatFecha(reserva.checkIn) }}</div>
                <div class="small text-muted"><i class="bi bi-box-arrow-right text-danger me-1"></i> Out: {{ formatFecha(reserva.checkOut) }}</div>
              </td>
              <td class="text-center">
                <span class="badge rounded-pill px-3 py-2 d-inline-flex align-items-center fw-normal text-capitalize" :class="getBadgeClass(reserva.estado)">
                  <i :class="getBadgeIcon(reserva.estado)" class="me-2"></i> {{ getNombreEstadoVisual(reserva.estado) }}
                </span>
              </td>
            </tr>

            <tr v-if="listaVisual.length === 0">
              <td colspan="4" class="text-center py-5 text-muted">
                <i class="bi bi-search display-4 mb-3 d-block text-light"></i>
                <p>No se encontraron resultados en esta categoría o con los filtros aplicados.</p>
                <button @click="limpiarFiltros" class="btn btn-sm btn-link text-success text-decoration-none fw-bold">
                  Ver todas las reservas
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.transition-all { transition: all 0.3s ease; }
.cursor-pointer { cursor: pointer; }
.cursor-pointer:hover { background-color: #f8f9fa !important; }
</style>