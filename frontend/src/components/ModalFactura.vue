<script setup>
import { ref, watch } from 'vue';
import apiClient from '@/api/apiClient'; // Importamos el cliente para hacer la petición

const props = defineProps({
  show: Boolean,
  reserva: Object
});

const emit = defineEmits(['close']);
const generando = ref(false);

// Nuevas variables para manejar los datos de la base de datos
const factura = ref(null);
const cargando = ref(false);
const errorMensaje = ref('');

// Magia reactiva: Cuando "show" cambie a true, buscamos la factura en el backend
watch(() => props.show, async (newVal) => {
  if (newVal && props.reserva) {
    cargando.value = true;
    errorMensaje.value = '';
    factura.value = null;

    try {
      const idReserva = props.reserva.id || props.reserva._id;
      // Consultamos el nuevo endpoint que creamos en Python
      const { data } = await apiClient.get(`/invoices/by-booking/${idReserva}`);
      factura.value = data;
    } catch (error) {
      console.error("Error al obtener la factura:", error);
      errorMensaje.value = "Aún no hay una cuenta de cobro abierta para esta reserva. Recuerda que la cuenta se genera automáticamente al hacer el Check-in (estado 'En Casa').";
    } finally {
      cargando.value = false;
    }
  }
});

const cerrar = () => {
  emit('close');
};

const descargarPDF = async () => {
  if (!factura.value) return;
  generando.value = true;

  try {
    const { default: html2pdf } = await import('html2pdf.js');
    const elemento = document.getElementById('documento-factura');

    const opciones = {
      margin: 10,
      filename: `Cuenta_Cobro_Kofan_${factura.value.guest_name || 'Cliente'}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    await html2pdf().set(opciones).from(elemento).save();
  } catch (error) {
    console.error('No se pudo generar el PDF:', error);
  } finally {
    generando.value = false;
  }
};

const formatoDinero = (valor) => {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);
};
</script>

<template>
  <div v-if="show" class="modal-overlay d-flex justify-content-center align-items-center" @click.self="cerrar">
    <div class="modal-box bg-white rounded-4 shadow-lg overflow-hidden" style="max-width: 800px; width: 95%; max-height: 90vh; display: flex; flex-direction: column;">
      
      <div class="bg-dark text-white p-3 d-flex justify-content-between align-items-center">
        <h5 class="mb-0 fw-bold"><font-awesome-icon :icon="['fas', 'file-pdf']" class="text-danger me-2" /> Estado de Cuenta</h5>
        <button @click="cerrar" class="btn btn-sm text-white fs-5 border-0 hover-danger">
          <font-awesome-icon icon="fa-solid fa-xmark" />
        </button>
      </div>

      <div class="p-4 overflow-auto bg-light" style="flex: 1;">
        
        <div v-if="cargando" class="text-center py-5">
          <div class="spinner-border text-success mb-3" role="status"></div>
          <p class="text-muted fw-bold">Consultando la cuenta del huésped...</p>
        </div>

        <div v-else-if="errorMensaje" class="text-center py-5 bg-white rounded shadow-sm border">
          <font-awesome-icon :icon="['fas', 'receipt']" class="display-1 text-muted opacity-50 mb-3" />
          <h5 class="fw-bold text-dark">Cuenta no encontrada</h5>
          <p class="text-muted w-75 mx-auto">{{ errorMensaje }}</p>
        </div>

        <div v-else-if="factura" id="documento-factura" class="bg-white p-5 border rounded shadow-sm" style="color: #333;">
          
          <div class="row border-bottom pb-3 mb-4 align-items-center">
            <div class="col-sm-6">
              <h2 class="fw-bold" style="color: #0f3b2a;">KOFÁN HOSPEDAJE</h2>
              <p class="mb-0 small">Puerto Asís, Putumayo - Colombia</p>
              <p class="mb-0 small">Cel: (+57) 322 4225925</p>
              <p class="mb-0 small">Email: kofancentroecoturistico@gmail.com</p>
            </div>
            <div class="col-sm-6 text-end">
              <h4 class="text-muted mb-1">CUENTA DE COBRO</h4>
              <p class="mb-0 fw-bold">Reserva ID: <span class="fw-normal">{{ factura.booking_id.slice(-6).toUpperCase() }}</span></p>
              <p class="mb-0 fw-bold">Fecha Emisión: <span class="fw-normal">{{ new Date(factura.issue_date || Date.now()).toLocaleDateString('es-CO') }}</span></p>
            </div>
          </div>

          <div class="row mb-4">
            <div class="col-12">
              <h6 class="fw-bold border-bottom pb-1" style="color: #0f3b2a;">Datos del Huésped</h6>
            </div>
            <div class="col-sm-6">
              <p class="mb-1"><strong>Nombre:</strong> {{ factura.guest_name }}</p>
              <p class="mb-1"><strong>Documento:</strong> CC {{ factura.guest_document }}</p>
            </div>
            <div class="col-sm-6 text-end">
              <p class="mb-1"><strong>Teléfono:</strong> {{ factura.guest_phone }}</p>
              <p class="mb-1"><strong>Email:</strong> {{ factura.guest_email }}</p>
            </div>
          </div>

          <h6 class="fw-bold border-bottom pb-1" style="color: #0f3b2a;">Detalle de Servicios</h6>
          <table class="table table-bordered table-sm mt-3">
            <thead class="table-light">
              <tr>
                <th>Descripción</th>
                <th class="text-center">Fechas</th>
                <th class="text-end">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Servicio de Alojamiento - {{ factura.room_name }}</td>
                <td class="text-center">{{ factura.check_in_date }} al {{ factura.check_out_date }}</td>
                <td class="text-end">{{ formatoDinero(factura.room_subtotal) }}</td>
              </tr>
              <tr v-for="(extra, index) in factura.extra_charges" :key="index">
                <td>Consumo: {{ extra.description }}</td>
                <td class="text-center">N/A</td>
                <td class="text-end">{{ formatoDinero(extra.amount) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="2" class="text-end fw-bold">TOTAL A PAGAR:</td>
                <td class="text-end fw-bold fs-5 text-success">{{ formatoDinero(factura.total_amount) }}</td>
              </tr>
            </tfoot>
          </table>

          <div class="mt-5 text-center text-muted small border-top pt-3">
            <p class="mb-0">¡Gracias por preferir Kofán Hospedaje!</p>
            <p class="mb-0">Este documento es un soporte de cobro interno y no reemplaza la factura electrónica si aplica.</p>
          </div>

        </div>
      </div>

      <div class="p-3 bg-light border-top text-end">
        <button type="button" class="btn btn-secondary me-2" @click="cerrar">Cerrar</button>
        <button type="button" class="btn btn-danger px-4" @click="descargarPDF" :disabled="generando || !factura">
          <span v-if="generando" class="spinner-border spinner-border-sm me-2"></span>
          <font-awesome-icon v-else :icon="['fas', 'file-pdf']" class="me-2" /> Descargar PDF
        </button>
      </div>

    </div>
  </div>
</template>


<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: rgba(0, 0, 0, 0.6); z-index: 1060; backdrop-filter: blur(4px);
}
.modal-box {
  animation: scaleIn 0.3s ease-out forwards;
}
@keyframes scaleIn {
  from { transform: scale(0.9) translateY(20px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}
/* Al imprimir a PDF, quitamos sombras para que quede plano y profesional */
#documento-factura {
  font-family: Arial, sans-serif;
}
</style>