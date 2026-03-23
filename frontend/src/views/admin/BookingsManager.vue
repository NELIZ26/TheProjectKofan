<script setup>
import { ref, computed, onMounted } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";

const reservas = ref([]);
const filtro = ref("");

const cargarReservas = async () => {
  try {
    const response = await apiClient.get("/api/reservas/admin/todas");
    console.log("Respuesta de FastAPI:", response.data); 
    reservas.value = response.data.reservas || response.data.data || response.data; 
  } catch (error) {
    console.error("Error al cargar reservas:", error);
  }
};

onMounted(() => {
  cargarReservas();
});

const reservasFiltradas = computed(() => {
  if (!filtro.value) return reservas.value;
  const termino = filtro.value.toLowerCase();
  
  return reservas.value.filter((res) => {
    const nombre = res.cliente_nombre ? res.cliente_nombre.toLowerCase() : "";
    const email = res.cliente_email ? res.cliente_email.toLowerCase() : "";
    const idReserva = res._id ? res._id.toLowerCase() : "";
    
    return nombre.includes(termino) || email.includes(termino) || idReserva.includes(termino);
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
    
    // 3. Si el administrador hizo clic en "Sí..."
    if (result.isConfirmed) {
      try {
        // Le avisamos a FastAPI
        await apiClient.patch(`/api/reservas/${id}/estado`, {
          estado: nuevoEstado,
          motivo_actualizacion: "Cambio de estado desde el panel de administrador"
        });

        // 🟢 MAGIA AQUÍ: Volvemos a pedir los datos a la BD. 
        // Esto actualiza la tabla al instante sin que el usuario presione F5.
        await cargarReservas();

        // Alerta de éxito pequeñita que desaparece sola
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

// 6. Eliminar / Cancelar (En hotelería es mejor "Cancelar" que "Borrar" de la BD)
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
      // Reutilizamos nuestra función para cambiar estado a "cancelada"
      actualizarEstado(id, "cancelada"); 
    }
  });
};

// 🟢 7. Helpers de colores (Alineados exactamente con los estados de tu FastAPI)
const getBadgeClass = (estado) => {
  // Aseguramos que el estado esté en minúsculas por si acaso
  const estadoLimpio = estado ? estado.toLowerCase() : "";
  
  switch (estadoLimpio) {
    case "confirmada":
      return "bg-success";
    case "ocupada": // El nuevo estado que agregamos
      return "bg-primary"; // O el color que prefieras para check-in
    case "pendiente":
      return "bg-warning text-dark";
    case "cancelada":
      return "bg-danger";
    case "finalizada":
      return "bg-secondary";
    default:
      return "bg-light text-dark";
  }
};

const verDetalles = (reserva) => {
  // 1. Calculamos la cantidad de noches mágicamente
  const fechaIn = new Date(reserva.fecha_entrada);
  const fechaOut = new Date(reserva.fecha_salida);
  const diferenciaTiempo = Math.abs(fechaOut - fechaIn);
  // Dividimos los milisegundos entre los milisegundos que tiene un día
  const noches = Math.ceil(diferenciaTiempo / (1000 * 60 * 60 * 24)); 

  // 2. Mostramos el modal
  Swal.fire({
    title: `Detalles de la Reserva`,
    html: `
      <div class="text-start" style="font-size: 0.95rem;">
        <p><strong>ID Reserva:</strong> <span class="text-muted">${reserva.id}</span></p>
        <p><strong>Cliente:</strong> ${reserva.cliente}</p>
        <p><strong>Habitación:</strong> ${reserva.habitacion}</p>
        <hr>
        <p><strong>Fecha de Entrada:</strong> ${reserva.fecha_entrada}</p>
        <p><strong>Fecha de Salida:</strong> ${reserva.fecha_salida}</p>
        <p><strong>Total de Noches:</strong> <span class="badge bg-secondary">${noches} noche(s)</span></p>
        <hr>
        <p><strong>Monto Total:</strong> <span class="text-success fw-bold">$${reserva.monto?.toLocaleString()}</span></p>
        <p><strong>Estado Actual:</strong> ${reserva.estado.toUpperCase()}</p>
      </div>
    `,
    icon: 'info',
    confirmButtonColor: "#0f3b2a"
  });
};

</script>

<template>
  <div class="bookings-manager">
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div
          class="card border-0 shadow-sm p-3 border-start border-4 border-success rounded-4"
        >
          <div class="d-flex align-items-center">
            <div
              class="icon-box bg-success-subtle p-3 rounded-3 me-3 text-success"
            >
              <font-awesome-icon icon="fa-solid fa-calendar-check" size="lg" />
            </div>
            <div>
              <h6 class="text-muted mb-0">Confirmadas</h6>
              <h4 class="fw-bold mb-0">
                {{ reservas.filter((r) => r.estado === "confirmada").length }}
              </h4>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div
          class="card border-0 shadow-sm p-3 border-start border-4 border-warning rounded-4"
        >
          <div class="d-flex align-items-center">
            <div
              class="icon-box bg-warning-subtle p-3 rounded-3 me-3 text-warning"
            >
              <font-awesome-icon icon="fa-solid fa-clock" size="lg" />
            </div>
            <div>
              <h6 class="text-muted mb-0">Pendientes</h6>
              <h4 class="fw-bold mb-0">
                {{ reservas.filter((r) => r.estado === "pendiente").length }}
              </h4>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div
          class="card border-0 shadow-sm p-3 border-start border-4 border-primary rounded-4"
        >
          <div class="d-flex align-items-center">
            <div
              class="icon-box bg-primary-subtle p-3 rounded-3 me-3 text-primary"
            >
              <font-awesome-icon
                icon="fa-solid fa-hand-holding-dollar"
                size="lg"
              />
            </div>
            <div>
              <h6 class="text-muted mb-0">Ingresos Proyectados</h6>
              <h4 class="fw-bold mb-0">
                ${{
                  reservas.reduce((acc, r) => acc + r.monto, 0).toLocaleString()
                }}
              </h4>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="card-header bg-white p-3 border-0">
        <div class="input-group">
          <span class="input-group-text bg-light border-0"
            ><font-awesome-icon icon="fa-solid fa-magnifying-glass"
          /></span>
          <input
            v-model="filtro"
            type="text"
            class="form-control bg-light border-0"
            placeholder="Buscar por cliente o ID de reserva..."
          />
        </div>
      </div>

      <div class="table-responsive">
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
            <tr v-for="res in reservasFiltradas" :key="res._id">
              <td>
                  <div class="fw-bold text-dark">RES-{{ res.id.slice(-6).toUpperCase() }}</div>
                  <div class="text-muted small">{{ res.cliente }}</div>
                </td>

                <td>{{ res.habitacion }}</td>

                <td>
                <div class="small text-muted"><strong>Entra:</strong> {{ res.fecha_entrada }}</div>
                <div class="small text-muted"><strong>Sale:</strong> {{ res.fecha_salida }}</div>
              </td>
              <td class="fw-bold text-success">
                ${{ res.monto.toLocaleString() }}
              </td>
              <td>
                <span
                  :class="[
                    'badge rounded-pill px-3',
                    getBadgeClass(res.estado),
                  ]"
                >
                  {{ res.estado }}
                </span>
              </td>
              <td class="text-center align-middle">
                <div class="d-flex justify-content-center gap-2">
                  <button v-if="res.estado === 'pendiente'" 
                            @click="actualizarEstado(res.id, 'confirmada')" 
                            class="btn btn-sm btn-outline-success" title="Confirmar Pago">
                      <i class="bi bi-check-lg"></i> </button>

                    <button v-if="res.estado === 'confirmada'" 
                            @click="actualizarEstado(res.id, 'ocupada')" 
                            class="btn btn-sm btn-outline-primary" title="Hacer Check-in">
                      <i class="bi bi-door-open"></i>
                    </button>

                    <button v-if="res.estado === 'ocupada'" 
                            @click="actualizarEstado(res.id, 'finalizada')" 
                            class="btn btn-sm btn-outline-secondary" title="Hacer Check-out">
                      <i class="bi bi-box-arrow-right"></i>
                    </button>

                    <button v-if="['pendiente', 'confirmada'].includes(res.estado)" 
                            @click="eliminarReserva(res.id)" 
                            class="btn btn-sm btn-outline-danger" title="Cancelar Reserva">
                      <i class="bi bi-x-lg"></i>
                    </button>

                    <button v-if="['finalizada', 'cancelada'].includes(res.estado)" 
                          @click="verDetalles(res)" 
                          class="btn btn-sm btn-outline-info" title="Ver Detalles completos">
                    <i class="bi bi-eye"></i> </button>

                    <button v-if="res.estado === 'cancelada'" 
                        @click="actualizarEstado(res.id, 'pendiente')" 
                        class="btn btn-sm btn-outline-warning" title="Restaurar Reserva">
                         <i class="bi bi-arrow-counterclockwise"></i> </button>
                  </div>
                </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
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
</style>
