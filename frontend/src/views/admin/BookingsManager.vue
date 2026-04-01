<script setup>
import { ref, computed, onMounted } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";
import ModalEdicionReserva from "@/components/ModalEdicionReserva.vue";
import ModalFactura from "@/components/ModalFactura.vue";

const reservas = ref([]);
const filtro = ref("");

// NUEVAS VARIABLES PARA TABS Y CARGA
const cargandoReservas = ref(true);
const pestanaActiva = ref("proximas"); 

const cargarReservas = async () => {
  cargandoReservas.value = true;
  try {
    const response = await apiClient.get("/api/reservas/admin/todas");
    reservas.value = response.data.reservas || response.data.data || response.data; 
  } catch (error) {
    console.error("Error al cargar reservas:", error);
    Swal.fire("Error", "No se pudieron cargar las reservas.", "error");
  } finally {
    setTimeout(() => {
      cargandoReservas.value = false;
    }, 300);
  }
};

onMounted(() => {
  cargarReservas();
});

// FILTRO MAESTRO
const reservasParaMostrar = computed(() => {
  let filtradas = reservas.value;

  // 1. Filtrar por Pestaña
  filtradas = filtradas.filter((res) => {
    const estado = (res.estado || "").toLowerCase();
    if (pestanaActiva.value === "proximas") return ["pendiente", "confirmada"].includes(estado);
    if (pestanaActiva.value === "casa") return estado === "ocupada"; 
    if (pestanaActiva.value === "historial") return ["finalizada", "cancelada"].includes(estado);
    return true;
  });

  // 2. Filtrar por Buscador
  if (filtro.value) {
    const termino = filtro.value.toLowerCase();
    filtradas = filtradas.filter((res) => {
      const nombre = (res.cliente || res.cliente_nombre || "").toLowerCase();
      const email = (res.cliente_email || "").toLowerCase();
      const idReserva = (res._id || res.id || "").toLowerCase();
      return nombre.includes(termino) || email.includes(termino) || idReserva.includes(termino);
    });
  }

  // 3. Ordenar
  return filtradas.sort((a, b) => {
    const idA = a.id || a._id || "";
    const idB = b.id || b._id || "";
    return idB.localeCompare(idA); 
  });
});

// 🟢 AQUÍ ESTABA EL ERROR: RESTAURAMOS LAS VARIABLES DE TEXTO
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
    texto = "¿El huésped ya llegó y se abrió su cuenta?";
    textoBoton = "Sí, hacer Check-in";
  } else if (nuevoEstado === 'finalizada') {
    titulo = "¿Hacer Check-out?";
    texto = "¿El huésped entregó la cabaña y se cerró su cuenta?";
    textoBoton = "Sí, finalizar";
  } else if (nuevoEstado === 'pendiente') {
    titulo = "¿Restaurar Reserva?";
    texto = "La reserva volverá a estar activa.";
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
        const datosReserva = reservas.value.find(r => (r.id || r._id) === id);

        // 1. Actualizamos el estado de la reserva
        await apiClient.patch(`/api/reservas/${id}/estado`, {
          estado: nuevoEstado,
          motivo_actualizacion: "Cambio de estado desde el panel"
        });

        // 2. SI ES CHECK-IN (ocupada), CREAMOS EL INVOICE
        if (nuevoEstado === 'ocupada' && datosReserva) {
          const payloadInvoice = {
            booking_id: id,
            guest_name: datosReserva.cliente_nombre || datosReserva.cliente,
            guest_document: datosReserva.cliente_documento || "N/A",
            guest_email: datosReserva.cliente_email || "N/A",
            guest_phone: datosReserva.cliente_celular || "N/A",
            room_name: datosReserva.habitacion_nombre || datosReserva.habitacion || "Habitación",
            check_in_date: datosReserva.fecha_entrada,
            check_out_date: datosReserva.fecha_salida,
            room_subtotal: datosReserva.monto_total || datosReserva.monto || 0,
            status: "open"
          };
          
          await apiClient.post("/invoices/", payloadInvoice);
        }

        // 🟢 3. SI ES CHECK-OUT (finalizada), CERRAMOS LA FACTURA
        if (nuevoEstado === 'finalizada') {
          try {
            await apiClient.put(`/invoices/close-by-booking/${id}`);
            console.log("Factura cerrada exitosamente");
          } catch (invoiceError) {
            console.warn("No se pudo cerrar la factura (quizás ya estaba cerrada o no existía).");
          }
        }

        await cargarReservas();
        Swal.fire({
          title: "¡Éxito!",
          text: nuevoEstado === 'ocupada' ? "Check-in realizado y cuenta abierta." : `La reserva ahora está ${nuevoEstado}.`,
          icon: "success",
          timer: 1500,
          showConfirmButton: false
        });
      } catch (error) {
        console.error("Error al actualizar:", error);
        Swal.fire("Error", "No se pudo actualizar el estado o crear la factura.", "error");
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
const esModoCheckIn = ref(false);

const abrirModalEdicion = (reserva, checkIn = false) => {
  reservaAEditar.value = reserva;
  esModoCheckIn.value = checkIn; 
  mostrarModalEdicion.value = true;
};

const refrescarTabla = async () => {
  await cargarReservas();
};

const mostrarModalFactura = ref(false);
const reservaParaFactura = ref(null);
const invoiceSeleccionada = ref(null);
const cargandoFactura = ref(false);

const abrirModalFactura = async (reserva) => {
  const idReserva = reserva.id || reserva._id;
  reservaParaFactura.value = reserva; 
  mostrarModalFactura.value = true;
  cargandoFactura.value = true;
  invoiceSeleccionada.value = null;

  try {
    const { data } = await apiClient.get(`/invoices/by-booking/${idReserva}`);
    invoiceSeleccionada.value = data;
  } catch (error) {
    console.error("No se encontró factura para esta reserva:", error);
  } finally {
    cargandoFactura.value = false;
  }
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
              <h4 class="fw-bold mb-0">${{ reservas.reduce((acc, r) => acc + (r.monto_total || r.monto || 0), 0).toLocaleString() }}</h4>
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
              <tr v-for="res in reservasParaMostrar" :key="res._id || res.id">
                <td>
                    <div class="fw-bold text-dark">RES-{{ (res.id || res._id || '').slice(-6).toUpperCase() }}</div>
                    <div class="text-dark fw-bold" style="font-size: 0.9rem;">{{ res.cliente || res.cliente_nombre }}</div>
                    <div class="text-muted mt-1" style="font-size: 0.75rem;">
                    <i class="bi bi-telephone-fill me-1"></i> {{ res.cliente_celular || 'Sin celular' }} <br>
                    <i class="bi bi-envelope-fill me-1"></i> {{ res.cliente_email || 'Sin correo' }}
                  </div>
                </td>
                <td>{{ res.habitacion || res.habitacion_nombre || 'N/A' }}</td>
                <td>
                  <div class="small text-muted"><strong>Entra:</strong> {{ res.fecha_entrada }}</div>
                  <div class="small text-muted"><strong>Sale:</strong> {{ res.fecha_salida }}</div>
                </td>
                <td class="fw-bold text-success">
                  ${{ (res.monto_total || res.monto || 0).toLocaleString() }}
                </td>
                <td>
                  <span :class="['badge rounded-pill px-3', getBadgeClass(res.estado)]">
                    {{ res.estado }}
                  </span>
                </td>
                <td class="text-center align-middle">
                <div class="d-flex justify-content-center gap-2">
                  
                  <button v-if="res.estado === 'pendiente'" 
                          @click="actualizarEstado(res.id || res._id, 'confirmada')" 
                          class="btn btn-sm btn-outline-success rounded-pill" title="Confirmar Pago">
                    <i class="bi bi-check-lg"></i>
                  </button>

                  <button v-if="['pendiente', 'confirmada'].includes(res.estado)" 
                          @click="eliminarReserva(res.id || res._id)" 
                          class="btn btn-sm btn-outline-danger rounded-pill" title="Cancelar Reserva">
                    <i class="bi bi-x-lg"></i>
                  </button>

                  <button v-if="res.estado === 'cancelada'" 
                      @click="actualizarEstado(res.id || res._id, 'pendiente')" 
                      class="btn btn-sm btn-outline-warning rounded-pill" title="Restaurar Reserva">
                      <i class="bi bi-arrow-counterclockwise"></i> 
                  </button>

                  <button v-if="res.estado === 'confirmada'" 
                          @click="abrirModalEdicion(res, true)" 
                          class="btn btn-sm btn-outline-primary rounded-pill fw-bold" title="Completar datos y Hacer Check-in">
                    <i class="bi bi-door-open"></i> Check-in
                  </button>

                  <button v-if="res.estado === 'ocupada'" 
                          @click="abrirModalEdicion(res, false)" 
                          class="btn btn-sm btn-outline-dark rounded-pill" title="Editar Detalles o Agregar Consumos">
                    <i class="bi bi-pencil-square"></i>
                  </button>

                  <button v-if="res.estado === 'ocupada'" 
                          @click="actualizarEstado(res.id || res._id, 'finalizada')" 
                          class="btn btn-sm btn-outline-secondary rounded-pill fw-bold" title="Hacer Check-out">
                    <i class="bi bi-box-arrow-right"></i> Check-out
                  </button>

                  <button v-if="res.estado === 'finalizada'" 
                    @click="abrirModalFactura(res)" 
                    class="btn btn-sm btn-outline-info rounded-pill" title="Ver Estado de Cuenta / Factura">
                    <i class="bi bi-receipt"></i>
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
      :modoCheckIn="esModoCheckIn"
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
