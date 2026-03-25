<script setup>
import { ref } from 'vue';
import html2pdf from 'html2pdf.js';

const props = defineProps({
  show: Boolean,
  reserva: Object
});

const emit = defineEmits(['close']);
const generando = ref(false);

const cerrar = () => {
  emit('close');
};

const descargarPDF = () => {
  generando.value = true;
  
  // Seleccionamos el div que contiene el diseño de la factura
  const elemento = document.getElementById('documento-factura');
  
  // Configuramos cómo queremos el PDF
  const opciones = {
    margin:       10,
    filename:     `Cuenta_Cobro_Kofan_${props.reserva.cliente_nombre || 'Cliente'}.pdf`,
    image:        { type: 'jpeg', quality: 0.98 },
    html2canvas:  { scale: 2, useCORS: true }, // scale: 2 mejora la resolución
    jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };

  // Magia: Convertir y descargar
  html2pdf().set(opciones).from(elemento).save().then(() => {
    generando.value = false;
  });
};

// Utilidad para formatear dinero
const formatoDinero = (valor) => {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);
};
</script>

<template>
  <div v-if="show" class="modal-overlay d-flex justify-content-center align-items-center" @click.self="cerrar">
    <div class="modal-box bg-white rounded-4 shadow-lg overflow-hidden" style="max-width: 800px; width: 95%; max-height: 90vh; display: flex; flex-direction: column;">
      
      <div class="bg-dark text-white p-3 d-flex justify-content-between align-items-center">
        <h5 class="mb-0 fw-bold"><i class="bi bi-file-earmark-pdf text-danger me-2"></i> Estado de Cuenta</h5>
        <button @click="cerrar" class="btn btn-sm text-white fs-5 border-0 hover-danger">
          <font-awesome-icon icon="fa-solid fa-times" />
        </button>
      </div>

      <div class="p-4 overflow-auto bg-light" style="flex: 1;">
        
        <div id="documento-factura" class="bg-white p-5 border rounded shadow-sm" style="color: #333;">
          
          <div class="row border-bottom pb-3 mb-4 align-items-center">
            <div class="col-sm-6">
              <h2 class="fw-bold" style="color: #0f3b2a;">KOFÁN HOSPEDAJE</h2>
              <p class="mb-0 small">Puerto Asís, Putumayo - Colombia</p>
              <p class="mb-0 small">Cel: (+57) 300 000 0000</p>
              <p class="mb-0 small">Email: contacto@kofanhospedaje.com</p>
            </div>
            <div class="col-sm-6 text-end">
              <h4 class="text-muted mb-1">CUENTA DE COBRO</h4>
              <p class="mb-0 fw-bold">Reserva ID: <span class="fw-normal">{{ reserva.id.slice(-6).toUpperCase() }}</span></p>
              <p class="mb-0 fw-bold">Fecha Emisión: <span class="fw-normal">{{ new Date().toLocaleDateString('es-CO') }}</span></p>
            </div>
          </div>

          <div class="row mb-4">
            <div class="col-12">
              <h6 class="fw-bold border-bottom pb-1" style="color: #0f3b2a;">Datos del Huésped</h6>
            </div>
            <div class="col-sm-6">
              <p class="mb-1"><strong>Nombre:</strong> {{ reserva.cliente_nombre || reserva.cliente }}</p>
              <p class="mb-1"><strong>Documento:</strong> {{ reserva.tipo_documento }} {{ reserva.cliente_documento }}</p>
            </div>
            <div class="col-sm-6 text-end">
              <p class="mb-1"><strong>Teléfono:</strong> {{ reserva.cliente_celular || 'N/A' }}</p>
              <p class="mb-1"><strong>Email:</strong> {{ reserva.cliente_email || 'N/A' }}</p>
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
                <td>Servicio de Alojamiento - {{ reserva.habitacion }}</td>
                <td class="text-center">{{ reserva.fecha_entrada }} al {{ reserva.fecha_salida }}</td>
                <td class="text-end">{{ formatoDinero(reserva.monto - (reserva.consumos_extras?.reduce((acc, c) => acc + c.valor, 0) || 0)) }}</td>
              </tr>
              <tr v-for="(extra, index) in reserva.consumos_extras" :key="index">
                <td>Consumo: {{ extra.concepto }}</td>
                <td class="text-center">N/A</td>
                <td class="text-end">{{ formatoDinero(extra.valor) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="2" class="text-end fw-bold">TOTAL A PAGAR:</td>
                <td class="text-end fw-bold fs-5 text-success">{{ formatoDinero(reserva.monto) }}</td>
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
        <button type="button" class="btn btn-danger px-4" @click="descargarPDF" :disabled="generando">
          <span v-if="generando" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-file-earmark-pdf-fill me-2"></i> Descargar PDF
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