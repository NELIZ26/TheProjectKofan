<script setup>
import { ref, computed, onMounted } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";
import ModalEdicionReserva from "@/components/ModalEdicionReserva.vue";
import ModalFactura from "@/components/ModalFactura.vue";

const reservas = ref([]);
const filtro = ref("");

// 🟢 NUEVAS VARIABLES PARA TABS Y CARGA
const cargandoReservas = ref(true);
const pestanaActiva = ref("proximas"); // 'proximas', 'casa', 'historial'

const cargarReservas = async () => {
  cargandoReservas.value = true; // Mostramos el spinner
  try {
    const response = await apiClient.get("/api/reservas/admin/todas");
    reservas.value = response.data.reservas || response.data.data || response.data; 
  } catch (error) {
    console.error("Error al cargar reservas:", error);
    Swal.fire("Error", "No se pudieron cargar las reservas.", "error");
  } finally {
    // Le damos un pequeño delay visual para que el spinner se vea suave
    setTimeout(() => {
      cargandoReservas.value = false;
    }, 300);
  }
};

onMounted(() => {
  cargarReservas();
});

// 🟢 FILTRO MAESTRO (Busca por texto, separa por pestaña y ordena por más nuevas)
const reservasParaMostrar = computed(() => {
  let filtradas = reservas.value;

  // 1. Filtrar por Pestaña
  filtradas = filtradas.filter((res) => {
    const estado = (res.estado || "").toLowerCase();
    if (pestanaActiva.value === "proximas") return ["pendiente", "confirmada"].includes(estado);
    if (pestanaActiva.value === "casa") return estado === "ocupada"; // "Ocupada" es Check-in en tu lógica
    if (pestanaActiva.value === "historial") return ["finalizada", "cancelada"].includes(estado);
    return true;
  });

  // 2. Filtrar por Buscador (Si hay algo escrito)
  if (filtro.value) {
    const termino = filtro.value.toLowerCase();
    filtradas = filtradas.filter((res) => {
      const nombre = (res.cliente || res.cliente_nombre || "").toLowerCase();
      const email = (res.cliente_email || "").toLowerCase();
      const idReserva = (res._id || res.id || "").toLowerCase();
      return nombre.includes(termino) || email.includes(termino) || idReserva.includes(termino);
    });
  }

  // 3. Ordenar: Las más nuevas creadas siempre de primeras (Usando el ID de Mongo)
  return filtradas.sort((a, b) => {
    const idA = a.id || a._id || "";
    const idB = b.id || b._id || "";
    return idB.localeCompare(idA); // Orden descendente cronológico
  });
});

const actualizarEstado = (id, nuevoEstado) => {
  let titulo = "¿Actualizar estado?";
  let texto = `¿Estás seguro de cambiar el estado a ${nuevoEstado}?`;
  let textoBoton = "Sí, cambiar";

  if (nuevoEstado === 'confirmada') {
    titulo = "¿Aprobar Pago?";
    texto = "Esto confirmará la reserva oficialmente.";
    textoBoton = "Sí, aprobar";
  } else if (nuevoEstado === 'ocupada') {
    titulo = "¿Hacer Check-in?";
    texto = "¿El huésped ya llegó y se le entregaron las llaves?";
    textoBoton = "Sí, hacer Check-in";
  } else if (nuevoEstado === 'finalizada') {
    titulo = "¿Hacer Check-out?";
    texto = "¿El huésped ya entregó la cabaña y se retiró?";
    textoBoton = "Sí, finalizar";
  }
  else if (nuevoEstado === 'pendiente') {
    titulo = "¿Restaurar Reserva?";
    texto = "La reserva volverá a estar activa (Pendiente). Asegúrate de que la cabaña siga libre en esas fechas.";
    textoBoton = "Sí, restaurar";
  }

  Swal.fire({
    title: titulo,
    text: texto,
    icon: "question",
    showCancelButton: true,
    confirmButtonColor: "#0f3b2a",
    cancelButtonColor: "#d33",
    confirmButtonText: textoBoton,
    cancelButtonText: "Cancelar"
  }).then(async (result) => {
    if (result.isConfirmed) {
      try {
        await apiClient.patch(`/api/reservas/${id}/estado`, {
          estado: nuevoEstado,
          motivo_actualizacion: "Cambio de estado desde el panel de administrador"
        });
        await cargarReservas();
        Swal.fire({
          title: "¡Éxito!",
          text: `La reserva ahora está ${nuevoEstado}.`,
          icon: "success",
          timer: 1500,
          showConfirmButton: false
        });
      } catch (error) {
        Swal.fire("Error", "Hubo un problema de conexión con el servidor.", "error");
      }
    }
  });
};

const eliminarReserva = (id) => {
  Swal.fire({
    title: "¿Cancelar Reserva?",
    text: "Esta acción marcará la reserva como cancelada y liberará la cabaña.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    confirmButtonText: "Sí, cancelar",
    cancelButtonText: "No, volver"
  }).then((result) => {
    if (result.isConfirmed) {
      actualizarEstado(id, "cancelada"); 
    }
  });
};

const getBadgeClass = (estado) => {
  const estadoLimpio = estado ? estado.toLowerCase() : "";
  switch (estadoLimpio) {
    case "confirmada": return "bg-success";
    case "ocupada": return "bg-primary"; 
    case "pendiente": return "bg-warning text-dark";
    case "cancelada": return "bg-danger";
    case "finalizada": return "bg-secondary";
    default: return "bg-light text-dark";
  }
};

const mostrarModalEdicion = ref(false);
const reservaAEditar = ref(null);

const abrirModalEdicion = (reserva) => {
  reservaAEditar.value = reserva;
  mostrarModalEdicion.value = true;
};

const refrescarTabla = async () => {
  await cargarReservas();
};

const mostrarModalFactura = ref(false);
const reservaParaFactura = ref(null);

const abrirModalFactura = (reserva) => {
  reservaParaFactura.value = reserva;
  mostrarModalFactura.value = true;
};
</script>

<template>
  <div class="bookings-manager container-fluid py-4">
    
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card border-0 shadow-sm p-3 border-start border-4 border-success rounded-4">
          <div class="d-flex align-items-center">
            <div class="icon-box bg-success-subtle p-3 rounded-3 me-3 text-success">
              <i class="bi bi-calendar-check fs-4"></i>
            </div>
            <div>
              <h6 class="text-muted mb-0">Confirmadas</h6>
              <h4 class="fw-bold mb-0">{{ reservas.filter((r) => r.estado === "confirmada").length }}</h4>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 shadow-sm p-3 border-start border-4 border-warning rounded-4">
          <div class="d-flex align-items-center">
            <div class="icon-box bg-warning-subtle p-3 rounded-3 me-3 text-warning">
              <i class="bi bi-clock fs-4"></i>
            </div>
            <div>
              <h6 class="text-muted mb-0">Pendientes</h6>
              <h4 class="fw-bold mb-0">{{ reservas.filter((r) => r.estado === "pendiente").length }}</h4>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 shadow-sm p-3 border-start border-4 border-primary rounded-4">
          <div class="d-flex align-items-center">
            <div class="icon-box bg-primary-subtle p-3 rounded-3 me-3 text-primary">
              <i class="bi bi-cash-stack fs-4"></i>
            </div>
            <div>
              <h6 class="text-muted mb-0">Ingresos Proyectados</h6>
              <h4 class="fw-bold mb-0">${{ reservas.reduce((acc, r) => acc + r.monto, 0).toLocaleString() }}</h4>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      
      <div class="card-header bg-white p-3 border-0 d-flex flex-column flex-md-row justify-content-between align-items-center gap-3">
        
        <ul class="nav nav-pills custom-tabs">
          <li class="nav-item">
            <button class="nav-link fw-bold" :class="{ 'active': pestanaActiva === 'proximas' }" @click="pestanaActiva = 'proximas'">
              <i class="bi bi-calendar-event me-1"></i> Por Llegar
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link fw-bold" :class="{ 'active': pestanaActiva === 'casa' }" @click="pestanaActiva = 'casa'">
              <i class="bi bi-house-door me-1"></i> En Casa
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link fw-bold" :class="{ 'active': pestanaActiva === 'historial' }" @click="pestanaActiva = 'historial'">
              <i class="bi bi-clock-history me-1"></i> Historial
            </button>
          </li>
        </ul>

        <div class="input-group" style="max-width: 350px;">
          <span class="input-group-text bg-light border-0"><i class="bi bi-search"></i></span>
          <input v-model="filtro" type="text" class="form-control bg-light border-0" placeholder="Buscar cliente o ID..." />
        </div>
      </div>

      <div class="card-body p-0 position-relative" style="min-height: 300px;">
        
        <div v-if="cargandoReservas" class="d-flex flex-column justify-content-center align-items-center h-100 position-absolute w-100 bg-white z-1" style="min-height: 300px;">
          <div class="spinner-border text-success" style="width: 3rem; height: 3rem;" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
          <p class="text-muted mt-3 fw-bold">Actualizando reservas...</p>
        </div>

        <div v-else-if="reservasParaMostrar.length === 0" class="d-flex flex-column justify-content-center align-items-center h-100 py-5">
          <i class="bi bi-folder-x display-1 text-light mb-3"></i>
          <h5 class="text-muted">No hay reservas en esta pestaña</h5>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-4">ID / Cliente</th>
                <th>Habitación</th>
                <th>Fechas (In - Out)</th>
                <th>Total</th>
                <th>Estado</th>
                <th class="text-center">ACCIONES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="res in reservasParaMostrar" :key="res._id">
                <td>
                    <div class="fw-bold text-dark">RES-{{ (res.id || res._id).slice(-6).toUpperCase() }}</div>
                    <div class="text-dark fw-bold" style="font-size: 0.9rem;">{{ res.cliente || res.cliente_nombre }}</div>
                    <div class="text-muted mt-1" style="font-size: 0.75rem;">
                    <i class="bi bi-telephone-fill me-1"></i> {{ res.cliente_celular || 'Sin celular' }} <br>
                    <i class="bi bi-envelope-fill me-1"></i> {{ res.cliente_email || 'Sin correo' }}
                  </div>
                </td>
                <td>{{ res.habitacion }}</td>
                <td>
                  <div class="small text-muted"><strong>Entra:</strong> {{ res.fecha_entrada }}</div>
                  <div class="small text-muted"><strong>Sale:</strong> {{ res.fecha_salida }}</div>
                </td>
                <td class="fw-bold text-success">
                  ${{ (res.monto || 0).toLocaleString() }}
                </td>
                <td>
                  <span :class="['badge rounded-pill px-3', getBadgeClass(res.estado)]">
                    {{ res.estado }}
                  </span>
                </td>
                <td class="text-center align-middle">
                  <div class="d-flex justify-content-center gap-2">
                    
                      <button v-if="['pendiente', 'confirmada', 'ocupada'].includes(res.estado)" 
                              @click="abrirModalEdicion(res)" 
                              class="btn btn-sm btn-outline-dark" title="Editar Detalles">
                        <i class="bi bi-pencil-square"></i>
                      </button>

                      <button v-if="res.estado === 'pendiente'" 
                              @click="actualizarEstado(res.id || res._id, 'confirmada')" 
                              class="btn btn-sm btn-outline-success" title="Confirmar Pago">
                        <i class="bi bi-check-lg"></i> 
                      </button>

                      <button v-if="res.estado === 'confirmada'" 
                              @click="actualizarEstado(res.id || res._id, 'ocupada')" 
                              class="btn btn-sm btn-outline-primary" title="Hacer Check-in">
                        <i class="bi bi-door-open"></i>
                      </button>

                      <button v-if="res.estado === 'ocupada'" 
                              @click="actualizarEstado(res.id || res._id, 'finalizada')" 
                              class="btn btn-sm btn-outline-secondary" title="Hacer Check-out">
                        <i class="bi bi-box-arrow-right"></i>
                      </button>

                      <button v-if="['pendiente', 'confirmada'].includes(res.estado)" 
                              @click="eliminarReserva(res.id || res._id)" 
                              class="btn btn-sm btn-outline-danger" title="Cancelar Reserva">
                        <i class="bi bi-x-lg"></i>
                      </button>

                      <button v-if="res.estado === 'finalizada'" 
                        @click="abrirModalFactura(res)" 
                        class="btn btn-sm btn-outline-info" title="Ver Factura">
                         <i class="bi bi-eye"></i>
                      </button>

                      <button v-if="res.estado === 'cancelada'" 
                          @click="actualizarEstado(res.id || res._id, 'pendiente')" 
                          class="btn btn-sm btn-outline-warning" title="Restaurar Reserva">
                           <i class="bi bi-arrow-counterclockwise"></i> 
                      </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <ModalEdicionReserva 
      :show="mostrarModalEdicion" 
      :reserva="reservaAEditar" 
      @close="mostrarModalEdicion = false" 
      @actualizado="refrescarTabla" 
    />
    <ModalFactura 
      :show="mostrarModalFactura" 
      :reserva="reservaParaFactura" 
      @close="mostrarModalFactura = false" 
    />
  </div>
</template>

<style scoped>

.bg-success-subtle {
  background-color: #d1e7dd;
}
.bg-warning-subtle {
  background-color: #fff3cd;
}
.bg-primary-subtle {
  background-color: #cfe2ff;
}

.icon-box {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table thead th {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.btn-group .btn:hover {
  background-color: #f8f9fa;
}

/* 🟢 ESTILOS PARA LAS PESTAÑAS (Nav-Pills) */
.custom-tabs .nav-link {
  color: #6c757d;
  background-color: transparent;
  border-radius: 50px;
  padding: 0.5rem 1.2rem;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}
.custom-tabs .nav-link:hover {
  background-color: #f8f9fa;
  color: #0f3b2a;
}
.custom-tabs .nav-link.active {
  background-color: #e8f5e9; /* Un verde súper suave */
  color: #0f3b2a; /* Verde oscuro Kofán */
  border-color: #0f3b2a;
}

</style>
