<script setup>
const paginaActual = ref(1);
const totalPaginas = ref(1);
const limitePorPagina = 10;
import { ref, computed, onMounted, watch } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";
import { defineAsyncComponent } from 'vue';
const ModalEdicionReserva = defineAsyncComponent(() => import('@/components/ModalEdicionReserva.vue'));
const ModalFactura = defineAsyncComponent(() => import('@/components/ModalFactura.vue'));

// 🟢 1. CONSTANTES (Eliminación de Magic Strings)
const ESTADOS_RESERVA = {
  PENDIENTE: "pendiente",
  CONFIRMADA: "confirmada",
  OCUPADA: "ocupada",
  FINALIZADA: "finalizada",
  CANCELADA: "cancelada"
};

const reservas = ref([]);
const filtro = ref("");
const filtroAplicado = ref(""); // Lo que realmente usaremos para filtrar
let timeoutBuscador = null; // Nuestro reloj temporizador

// Vigilar cada vez que el usuario teclea en "filtro"
watch(filtro, (nuevoValor) => {
  clearTimeout(timeoutBuscador); // Cancelar la búsqueda anterior si sigue tecleando
  
  timeoutBuscador = setTimeout(() => {
    filtroAplicado.value = nuevoValor; // Aplicar la búsqueda real después de 300ms (0.3 seg)
  }, 300);
});
const cargandoReservas = ref(true);
const pestanaActiva = ref("proximas"); 

const cargarReservas = async () => {
  cargandoReservas.value = true;
  try {
    // 1. Armamos el texto que le vamos a enviar al backend según la pestaña
    let estadosQuery = "";
    if (pestanaActiva.value === "proximas") estadosQuery = `${ESTADOS_RESERVA.PENDIENTE},${ESTADOS_RESERVA.CONFIRMADA}`;
    if (pestanaActiva.value === "casa") estadosQuery = ESTADOS_RESERVA.OCUPADA;
    if (pestanaActiva.value === "historial") estadosQuery = `${ESTADOS_RESERVA.FINALIZADA},${ESTADOS_RESERVA.CANCELADA}`;

    // 🟢 2. EL FIX ESTÁ AQUÍ: Mira bien que la URL ahora incluye ?estados=${estadosQuery}
    const response = await apiClient.get(`/api/reservas/admin/todas?estados=${estadosQuery}&page=${paginaActual.value}&limit=${limitePorPagina}`);
    
    reservas.value = response.data.reservas || response.data.data || response.data; 
    
    // 3. Sincronizamos la paginación
    if (response.data.resumen) {
      totalPaginas.value = response.data.resumen.total_paginas || 1;
      paginaActual.value = response.data.resumen.pagina_actual || paginaActual.value;
    }
  } catch (error) {
    console.error("Error al cargar reservas:", error);
    Swal.fire("Error", "No se pudieron cargar las reservas.", "error");
  } finally {
    setTimeout(() => { cargandoReservas.value = false; }, 300);
  }
};

// 🟢 Agrega esta nueva función para cambiar de página
const cambiarPestana = (nuevaPestana) => {
  pestanaActiva.value = nuevaPestana; 
  paginaActual.value = 1;             
  cargarReservas();                 
};
const cambiarPagina = (nuevaPagina) => {
  // Solo avanza o retrocede si la página destino existe
  if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas.value) {
    paginaActual.value = nuevaPagina; // Actualiza el número
    cargarReservas();                 // Llama al backend pidiendo el nuevo bloque de 10
  }
};

onMounted(() => {
  cargarReservas();
});

// FILTRO MAESTRO
const reservasParaMostrar = computed(() => {
  let filtradas = reservas.value; 

  // Ya no filtramos por pestaña aquí, solo dejamos el buscador de texto
  if (filtroAplicado.value) {
    const termino = filtroAplicado.value.toLowerCase();
    filtradas = filtradas.filter((res) => {
      const nombre = (res.cliente || res.cliente_nombre || "").toLowerCase();
      const email = (res.cliente_email || "").toLowerCase();
      const idReserva = (res._id || res.id || "").toLowerCase();
      return nombre.includes(termino) || email.includes(termino) || idReserva.includes(termino);
    });
  }

  return filtradas; 
});

// 🟢 2. SEPARACIÓN DE LÓGICA: Solo llamadas a la API
const procesarCambioEstadoAPI = async (id, nuevoEstado, datosReserva) => {
  // 1. Actualizamos el estado de la reserva
  await apiClient.patch(`/api/reservas/${id}/estado`, {
    estado: nuevoEstado,
    motivo_actualizacion: "Cambio de estado desde el panel"
  });

  // 2. SI ES CHECK-IN, CREAMOS EL INVOICE
  if (nuevoEstado === ESTADOS_RESERVA.OCUPADA && datosReserva) {
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

  // 3. SI ES CHECK-OUT, CERRAMOS LA FACTURA
  if (nuevoEstado === ESTADOS_RESERVA.FINALIZADA) {
    try {
      await apiClient.put(`/invoices/close-by-booking/${id}`);
      console.log("Factura cerrada exitosamente");
    } catch (invoiceError) {
      console.warn("No se pudo cerrar la factura (quizás ya estaba cerrada o no existía).");
    }
  }
};

// 🟢 3. SEPARACIÓN DE LÓGICA: Solo Interfaz de Usuario (SweetAlert)
const actualizarEstado = (id, nuevoEstado) => {
  let titulo = "¿Actualizar estado?";
  let texto = `¿Estás seguro de cambiar el estado a ${nuevoEstado}?`;
  let textoBoton = "Sí, cambiar";

  if (nuevoEstado === ESTADOS_RESERVA.CONFIRMADA) {
    titulo = "¿Aprobar Pago?";
    texto = "Esto confirmará la reserva oficialmente.";
    textoBoton = "Sí, aprobar";
  } else if (nuevoEstado === ESTADOS_RESERVA.OCUPADA) {
    titulo = "¿Hacer Check-in?";
    texto = "¿El huésped ya llegó y se abrió su cuenta?";
    textoBoton = "Sí, hacer Check-in";
  } else if (nuevoEstado === ESTADOS_RESERVA.FINALIZADA) {
    titulo = "¿Hacer Check-out?";
    texto = "¿El huésped entregó la cabaña y se cerró su cuenta?";
    textoBoton = "Sí, finalizar";
  } else if (nuevoEstado === ESTADOS_RESERVA.PENDIENTE) {
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
        
        // Llamamos a la función de API separada
        await procesarCambioEstadoAPI(id, nuevoEstado, datosReserva);
        await cargarReservas();
        
        Swal.fire({
          title: "¡Éxito!",
          text: nuevoEstado === ESTADOS_RESERVA.OCUPADA ? "Check-in realizado y cuenta abierta." : `La reserva ahora está ${nuevoEstado}.`,
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
      actualizarEstado(id, ESTADOS_RESERVA.CANCELADA); 
    }
  });
};

// 🟢 Función actualizada para el fondo y borde (Estilo Kofán)
const getBadgeClass = (estado) => {
  switch (estado) {
    case ESTADOS_RESERVA.CONFIRMADA:
      return 'bg-success bg-opacity-10 text-success border border-success';
    case ESTADOS_RESERVA.PENDIENTE:
      return 'bg-warning bg-opacity-10 text-warning border border-warning';
    case ESTADOS_RESERVA.OCUPADA:
      return 'bg-primary bg-opacity-10 text-primary border border-primary';
    case ESTADOS_RESERVA.FINALIZADA:
      return 'bg-secondary bg-opacity-10 text-secondary border border-secondary';
    case ESTADOS_RESERVA.CANCELADA:
      return 'bg-danger bg-opacity-10 text-danger border border-danger';
    default:
      return 'bg-light text-dark border border-secondary';
  }
};

// 🟢 Nueva función para los iconos
const getBadgeIcon = (estado) => {
  switch (estado) {
    case ESTADOS_RESERVA.CONFIRMADA:
      return 'bi bi-check-circle-fill';
    case ESTADOS_RESERVA.PENDIENTE:
      return 'bi bi-clock-fill';
    case ESTADOS_RESERVA.OCUPADA:
      return 'bi bi-house-door-fill';
    case ESTADOS_RESERVA.FINALIZADA:
      return 'bi bi-check2-all';
    case ESTADOS_RESERVA.CANCELADA:
      return 'bi bi-x-circle-fill';
    default:
      return 'bi bi-info-circle-fill';
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
              <h4 class="fw-bold mb-0">{{ reservas.filter((r) => r.estado === ESTADOS_RESERVA.CONFIRMADA).length }}</h4>
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
              <h4 class="fw-bold mb-0">{{ reservas.filter((r) => r.estado === ESTADOS_RESERVA.PENDIENTE).length }}</h4>
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
        
        <div class="bg-light p-1 rounded-pill d-flex border shadow-sm">
          <button 
            class="btn rounded-pill px-4 fw-bold border-0 transition-all" 
            :class="pestanaActiva === 'proximas' ? 'btn-dark text-white shadow' : 'text-muted'" 
            @click="cambiarPestana('proximas')"
          >
            <i class="bi bi-calendar-event me-2"></i> Por Llegar
          </button>
          
          <button 
            class="btn rounded-pill px-4 fw-bold border-0 transition-all" 
            :class="pestanaActiva === 'casa' ? 'btn-dark text-white shadow' : 'text-muted'" 
            @click="cambiarPestana('casa')"
          >
            <i class="bi bi-house-door me-2"></i> En Casa
          </button>
          
          <button 
            class="btn rounded-pill px-4 fw-bold border-0 transition-all" 
            :class="pestanaActiva === 'historial' ? 'btn-dark text-white shadow' : 'text-muted'" 
            @click="cambiarPestana('historial')"
          >
            <i class="bi bi-clock-history me-2"></i> Historial
          </button>
        </div>

        <div class="input-group shadow-sm rounded-pill overflow-hidden" style="max-width: 350px;">
          <span class="input-group-text bg-light border-0 ps-3"><i class="bi bi-search text-muted"></i></span>
          <input v-model="filtro" type="text" class="form-control bg-light border-0 shadow-none" placeholder="Buscar cliente o ID..." />
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
                <th class="ps-4 py-3 text-muted small fw-bold">ID / CLIENTE</th>
                <th class="py-3 text-muted small fw-bold">HABITACIÓN</th>
                <th class="py-3 text-muted small fw-bold">FECHAS (IN - OUT)</th>
                <th class="py-3 text-muted small fw-bold">TOTAL</th>
                <th class="py-3 text-muted small fw-bold">ESTADO</th>
                <th class="text-center py-3 text-muted small fw-bold">ACCIONES</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="res in reservasParaMostrar" :key="res._id || res.id">
                <td class="ps-4">
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
                <span 
                  class="badge rounded-pill px-3 py-2 d-inline-flex align-items-center fw-normal text-capitalize" 
                  :class="getBadgeClass(res.estado)"
                >
                  <i :class="getBadgeIcon(res.estado)" class="me-2"></i>
                  {{ res.estado }}
                </span>
              </td>
                <td class="text-center align-middle">
                
                <div class="d-flex justify-content-center gap-2">
                  
                  <button v-if="res.estado === ESTADOS_RESERVA.PENDIENTE" 
                          @click="actualizarEstado(res.id || res._id, ESTADOS_RESERVA.CONFIRMADA)" 
                          class="btn btn-sm btn-outline-success rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                          style="width: 35px; height: 35px;" title="Confirmar Pago">
                    <i class="bi bi-check-lg fs-6"></i>
                  </button>

                  <button v-if="[ESTADOS_RESERVA.PENDIENTE, ESTADOS_RESERVA.CONFIRMADA].includes(res.estado)" 
                          @click="eliminarReserva(res.id || res._id)" 
                          class="btn btn-sm btn-outline-danger rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                          style="width: 35px; height: 35px;" title="Cancelar Reserva">
                    <i class="bi bi-x-lg fs-6"></i>
                  </button>

                  <button v-if="res.estado === ESTADOS_RESERVA.CANCELADA" 
                      @click="actualizarEstado(res.id || res._id, ESTADOS_RESERVA.PENDIENTE)" 
                      class="btn btn-sm btn-outline-warning rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                      style="width: 35px; height: 35px;" title="Restaurar Reserva">
                      <i class="bi bi-arrow-counterclockwise fs-6"></i> 
                  </button>

                  <button v-if="res.estado === ESTADOS_RESERVA.CONFIRMADA" 
                          @click="abrirModalEdicion(res, true)" 
                          class="btn btn-sm btn-outline-primary rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                          style="width: 35px; height: 35px;" title="Hacer Check-in">
                    <i class="bi bi-door-open fs-6"></i>
                  </button>

                  <button v-if="res.estado === ESTADOS_RESERVA.OCUPADA" 
                          @click="abrirModalEdicion(res, false)" 
                          class="btn btn-sm btn-outline-dark rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                          style="width: 35px; height: 35px;" title="Editar Detalles o Agregar Consumos">
                    <i class="bi bi-pencil-square fs-6"></i>
                  </button>

                  <button v-if="res.estado === ESTADOS_RESERVA.OCUPADA" 
                          @click="actualizarEstado(res.id || res._id, ESTADOS_RESERVA.FINALIZADA)" 
                          class="btn btn-sm btn-outline-secondary rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                          style="width: 35px; height: 35px;" title="Hacer Check-out">
                    <i class="bi bi-box-arrow-right fs-6"></i>
                  </button>

                  <button v-if="res.estado === ESTADOS_RESERVA.FINALIZADA" 
                    @click="abrirModalFactura(res)" 
                    class="btn btn-sm btn-outline-info rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                    style="width: 35px; height: 35px;" title="Ver Estado de Cuenta / Factura">
                    <i class="bi bi-receipt fs-6"></i>
                  </button>

                </div>
              </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="totalPaginas > 1" class="d-flex flex-column flex-md-row justify-content-between align-items-center p-3 bg-light border-top">
          <span class="text-muted small fw-bold mb-2 mb-md-0">
            Mostrando página {{ paginaActual }} de {{ totalPaginas }}
          </span>
          <div class="btn-group shadow-sm">
            <button 
              @click="cambiarPagina(paginaActual - 1)" 
              :disabled="paginaActual === 1" 
              class="btn btn-sm btn-white border">
              <i class="bi bi-chevron-left me-1"></i> Anterior
            </button>
            <button 
              @click="cambiarPagina(paginaActual + 1)" 
              :disabled="paginaActual === totalPaginas" 
              class="btn btn-sm btn-white border">
              Siguiente <i class="bi bi-chevron-right ms-1"></i>
            </button>
          </div>
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
