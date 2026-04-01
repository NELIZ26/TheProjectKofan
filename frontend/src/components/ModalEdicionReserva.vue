<script setup>
import { ref, reactive, watch } from 'vue';
import Swal from 'sweetalert2';
import apiClient from '@/api/apiClient';

const props = defineProps({
  show: Boolean,
  reserva: Object,
  modoCheckIn: { type: Boolean, default: false }
});

const emit = defineEmits(['close', 'actualizado']);
const guardando = ref(false);

// El estado del formulario basado en tu esquema de FastAPI
// 1. Agregamos consumos_extras al formulario y una variable para el precio por noche
// 1. Agregamos consumos_extras como una lista (array)
const form = reactive({
  cliente_nombre: '',
  cliente_email: '',
  cliente_celular: '',
  tipo_documento: '',
  cliente_documento: '',
  fecha_entrada: '', 
  fecha_salida: '',  
  monto_total: 0,    
  consumos_extras: [], // 🟢 AHORA ES UNA LISTA
  acompanantes: []
});

const precioPorNoche = ref(0);

// 🟢 FUNCIONES PARA LOS EXTRAS
const agregarConsumo = () => {
  // Los nuevos nacen con "bloqueado: false" para poder escribirlos
  form.consumos_extras.push({ concepto: '', valor: '', bloqueado: false });
};

const quitarConsumo = (index) => {
  form.consumos_extras.splice(index, 1);
};

// 🟢 RECALCULAR EL GRAN TOTAL AUTOMÁTICAMENTE
const recalcularTotal = () => {
  if (form.fecha_entrada && form.fecha_salida) {
    const fIn = new Date(form.fecha_entrada);
    const fOut = new Date(form.fecha_salida);
    
    if (fOut > fIn) {
      // 1. Calculamos las noches
      const nuevasNoches = Math.ceil(Math.abs(fOut - fIn) / (1000 * 60 * 60 * 24));
      
      // 2. Sumamos todo lo de la lista de extras
      const totalExtras = form.consumos_extras.reduce((acc, item) => acc + Number(item.valor || 0), 0);
      
      // 3. El Gran Total
      form.monto_total = (nuevasNoches * precioPorNoche.value) + totalExtras;
    }
  }
};

// Observamos si el admin cambia la fecha de salida o mueve algún valor de los extras
watch(() => form.fecha_salida, recalcularTotal);
watch(() => form.consumos_extras, recalcularTotal, { deep: true }); // deep: true observa los cambios dentro de la lista

// 2. Cargamos los datos al abrir el modal
watch(() => props.show, async (newVal) => {
  if (newVal && props.reserva) {
    form.cliente_nombre = props.reserva.cliente || props.reserva.cliente_nombre || '';
    form.cliente_email = props.reserva.cliente_email || '';
    form.cliente_celular = props.reserva.cliente_celular || '';
    form.tipo_documento = props.reserva.tipo_documento === "Pendiente" ? "" : (props.reserva.tipo_documento || "");
    form.cliente_documento = props.reserva.cliente_documento === "0" ? "" : (props.reserva.cliente_documento || "");
    
    // Clonamos acompañantes (estos sí se quedan en la reserva)
    form.acompanantes = props.reserva.acompanantes 
      ? JSON.parse(JSON.stringify(props.reserva.acompanantes)).map(acomp => ({ ...acomp, bloqueado: true }))
      : [];

    // 🟢 AHORA CONSULTAMOS LOS EXTRAS DIRECTAMENTE DESDE LA FACTURA
    form.consumos_extras = []; // Limpiamos la lista por defecto
    try {
      const idReserva = props.reserva.id || props.reserva._id;
      const { data } = await apiClient.get(`/invoices/by-booking/${idReserva}`);
      
      // Si la factura existe y tiene cargos, los mapeamos al formulario
      if (data && data.extra_charges) {
        form.consumos_extras = data.extra_charges.map(extra => ({
          concepto: extra.description,
          valor: extra.amount,
          bloqueado: true // Los bloqueamos para que no se editen desde aquí
        }));
      }
    } catch (error) {
      // Es normal que falle si el huésped aún no tiene Check-in (no hay factura)
    }

    form.fecha_entrada = props.reserva.fecha_entrada || '';
    form.fecha_salida = props.reserva.fecha_salida || '';
    form.monto_total = props.reserva.monto || props.reserva.monto_total || 0;

    // Calculamos el precio base por noche
    const fIn = new Date(form.fecha_entrada);
    const fOut = new Date(form.fecha_salida);
    const nochesOriginales = Math.max(1, Math.ceil(Math.abs(fOut - fIn) / (1000 * 60 * 60 * 24)));
    
    const extrasOriginales = form.consumos_extras.reduce((acc, item) => acc + Number(item.valor || 0), 0);
    const costoHabitacion = form.monto_total - extrasOriginales;
    
    precioPorNoche.value = costoHabitacion / nochesOriginales;
  }
});

// En tu payload de guardarDetalles(), no olvides añadir consumos_extras: Number(form.consumos_extras)

const agregarAcompanante = () => {
  form.acompanantes.push({ 
    nombre_completo: '', 
    tipo_documento: '', 
    numero_documento: '', 
    parentesco: '', 
    bloqueado: false // 🟢 Nace libre para ser editado
  });
};

const quitarAcompanante = (index) => {
  form.acompanantes.splice(index, 1);
};

const guardarDetalles = async () => {
  guardando.value = true;
  try {
    const idReserva = props.reserva.id || props.reserva._id;
    
    // 1. Calculamos los totales
    const totalExtras = form.consumos_extras.reduce((acc, e) => acc + Number(e.valor || 0), 0);
    const subtotalHabitacion = Number(form.monto_total) - totalExtras;
    const extrasParaFactura = form.consumos_extras.map(e => ({ concepto: e.concepto, valor: Number(e.valor) }));

    // 2. Preparamos el payload de la reserva
    const payloadReserva = {
      cliente_nombre: form.cliente_nombre,
      cliente_email: form.cliente_email,
      cliente_celular: form.cliente_celular,
      tipo_documento: form.tipo_documento || "CC",
      cliente_documento: form.cliente_documento || "0",
      fecha_entrada: form.fecha_entrada,
      fecha_salida: form.fecha_salida,
      monto_total: Number(form.monto_total),
      acompanantes: form.acompanantes.map(a => ({
        nombre_completo: a.nombre_completo,
        tipo_documento: a.tipo_documento,
        numero_documento: a.numero_documento,
        parentesco: a.parentesco
      })),
    };

    // 3. Guardamos los datos de la reserva siempre
    await apiClient.put(`/api/reservas/${idReserva}/detalles`, payloadReserva);

    // 🟢 4. BIFURCACIÓN: ¿Es Check-in o es Edición normal?
    if (props.modoCheckIn) {
      
      // A. Cambiamos el estado a 'ocupada'
      await apiClient.patch(`/api/reservas/${idReserva}/estado`, {
        estado: 'ocupada',
        motivo_actualizacion: "Check-in realizado en recepción"
      });

      // B. Nace la factura
      await apiClient.post("/invoices/", {
        booking_id: idReserva,
        guest_name: form.cliente_nombre,
        guest_document: form.cliente_documento,
        guest_email: form.cliente_email,
        guest_phone: form.cliente_celular,
        room_name: props.reserva.habitacion_nombre || props.reserva.habitacion || "Habitación",
        check_in_date: form.fecha_entrada,
        check_out_date: form.fecha_salida,
        room_subtotal: subtotalHabitacion,
        status: "open",
        extra_charges: extrasParaFactura
      });

      Swal.fire({
        icon: 'success',
        title: '¡Check-in Exitoso!',
        text: 'El huésped ya está registrado y su cuenta está abierta.',
        timer: 2000,
        showConfirmButton: false
      });

    } else {
      // Es una edición normal (sincronizar factura)
      try {
        await apiClient.put(`/invoices/sync-by-booking/${idReserva}`, {
          check_out_date: form.fecha_salida,
          room_subtotal: subtotalHabitacion,
          total_amount: Number(form.monto_total),
          extra_charges: extrasParaFactura 
        });
      } catch (invoiceError) {
        console.warn("Aviso:", "El huésped aún no tiene cuenta abierta.");
      }

      Swal.fire({
        icon: 'success',
        title: '¡Guardado!',
        text: 'Los detalles se actualizaron correctamente.',
        timer: 1500,
        showConfirmButton: false
      });
    }

    emit('actualizado'); 
    cerrar();
  } catch (error) {
    console.error("Error al guardar/check-in:", error);
    Swal.fire('Error', 'Hubo un problema al procesar la solicitud.', 'error');
  } finally {
    guardando.value = false;
  }
};

const cerrar = () => {
  emit('close');
};
</script>

<template>
  <div v-if="show" class="modal-overlay d-flex justify-content-center align-items-center" @click.self="cerrar">
    <div class="modal-box bg-white rounded-4 shadow-lg overflow-hidden" style="max-width: 800px; width: 95%; max-height: 90vh; display: flex; flex-direction: column;">
      
      <div class="bg-dark text-white p-3 d-flex justify-content-between align-items-center border-bottom border-success border-3">
        <h5 class="mb-0 fw-bold d-flex align-items-center">
        <font-awesome-icon :icon="modoCheckIn ? 'fa-solid fa-door-open' : 'fa-solid fa-user-pen'" class="text-success me-3 fs-4" />
        {{ modoCheckIn ? 'Realizar Check-in:' : 'Completar Datos:' }} {{ form.cliente_nombre }}
      </h5>
        <button @click="cerrar" class="btn btn-sm text-white fs-5 border-0 hover-danger">
          <font-awesome-icon icon="fa-solid fa-times" />
        </button>
      </div>

      <div class="p-4 overflow-auto" style="flex: 1;">
        <form @submit.prevent="guardarDetalles" id="formEdicionReserva">
          
          <h6 class="fw-bold text-success mb-3 border-bottom pb-2">Datos del Titular</h6>
          <h6 class="fw-bold text-success mb-3 border-bottom pb-2">Estadía y Cobro</h6>
          <div class="row g-3 mb-4 bg-light p-3 rounded border">
            <div class="col-md-4">
              <label class="form-label small fw-bold text-muted">Ingreso <i class="bi bi-lock-fill text-warning"></i></label>
              <input type="date" class="form-control bg-white text-muted" v-model="form.fecha_entrada" disabled readonly>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold text-success">Salida (Extender)</label>
              <input type="date" class="form-control border-success" v-model="form.fecha_salida" required>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold text-dark">Gran Total a Cobrar</label>
              <input type="number" class="form-control fw-bold bg-white text-dark" v-model="form.monto_total" readonly>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2 mt-4">
            <h6 class="fw-bold text-success mb-0">Consumos Extras (Minibar, Restaurante, etc.)</h6>
            <button type="button" class="btn btn-sm btn-outline-success" @click="agregarConsumo">
              <font-awesome-icon icon="fa-solid fa-plus" /> Agregar Extra
            </button>
          </div>

          <div v-if="form.consumos_extras.length === 0" class="text-center p-3 bg-light rounded text-muted small mb-4">
            No hay consumos extras registrados.
          </div>

          <div v-for="(extra, index) in form.consumos_extras" :key="'extra-'+index" class="row g-2 mb-3 p-3 border rounded position-relative" :class="extra.bloqueado ? 'bg-secondary bg-opacity-10 border-secondary' : 'bg-light'">
            
            <button v-if="!extra.bloqueado" type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-2" style="width: 30px; height: 30px; padding: 0;" @click="quitarConsumo(index)">
              <font-awesome-icon icon="fa-solid fa-trash" />
            </button>
            
            <div class="col-md-8">
              <label class="form-label small fw-bold text-muted">Concepto</label>
              <input type="text" class="form-control form-control-sm" :class="{'bg-white': extra.bloqueado}" placeholder="Ej: 2 Cervezas, 1 Desayuno..." v-model="extra.concepto" :disabled="extra.bloqueado" required>
            </div>
            <div class="col-md-4">
              <label class="form-label small fw-bold text-muted">Valor ($)</label>
              <input type="number" class="form-control form-control-sm" :class="{'bg-white': extra.bloqueado}" placeholder="Ej: 15000" v-model="extra.valor" :disabled="extra.bloqueado" required min="0">
            </div>
            
            <div v-if="extra.bloqueado" class="col-12 mt-1">
              <small class="text-success"><i class="bi bi-check-circle-fill"></i> Registrado en cuenta</small>
            </div>
          </div>
          <div class="row g-3 mb-4">
            <div class="col-md-12">
              <label class="form-label small fw-bold text-muted">Nombre Completo / Razón Social</label>
              <input type="text" class="form-control" v-model="form.cliente_nombre" required>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold text-muted">Tipo Documento</label>
              <select class="form-select" v-model="form.tipo_documento" required>
                <option value="" disabled>Seleccione...</option>
                <option value="CC">Cédula de Ciudadanía</option>
                <option value="CE">Cédula de Extranjería</option>
                <option value="PA">Pasaporte</option>
                <option value="NIT">NIT</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold text-muted">Número de Documento</label>
              <input type="text" class="form-control" v-model="form.cliente_documento" required>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold text-muted">Celular</label>
              <input type="tel" class="form-control" v-model="form.cliente_celular" required>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold text-muted">Correo Electrónico</label>
              <input type="email" class="form-control" v-model="form.cliente_email" required>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2 mt-4">
            <h6 class="fw-bold text-success mb-0">Registro de Acompañantes</h6>
            <button type="button" class="btn btn-sm btn-outline-success" @click="agregarAcompanante">
              <font-awesome-icon icon="fa-solid fa-plus" /> Agregar
            </button>
          </div>

          <div v-if="form.acompanantes.length === 0" class="text-center p-3 bg-light rounded text-muted small">
            No hay acompañantes registrados. Presiona "Agregar" si vienen más personas.
          </div>

          <div v-for="(acomp, index) in form.acompanantes" :key="'acomp-'+index" class="row g-2 mb-3 p-3 border rounded position-relative" :class="acomp.bloqueado ? 'bg-secondary bg-opacity-10 border-secondary' : 'bg-light'">
            
            <button v-if="!acomp.bloqueado" type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-2" style="width: 30px; height: 30px; padding: 0;" @click="quitarAcompanante(index)">
              <font-awesome-icon icon="fa-solid fa-trash" />
            </button>
            
            <div class="col-12">
              <strong class="small text-dark">Acompañante {{ index + 1 }}</strong>
            </div>
            
            <div class="col-md-6">
              <input type="text" class="form-control form-control-sm" :class="{'bg-white': acomp.bloqueado}" placeholder="Nombre completo" v-model="acomp.nombre_completo" :disabled="acomp.bloqueado" required>
            </div>
            <div class="col-md-3">
              <select class="form-select form-select-sm" :class="{'bg-white': acomp.bloqueado}" v-model="acomp.tipo_documento" :disabled="acomp.bloqueado" required>
                <option value="" disabled>Tipo ID...</option>
                <option value="CC">C.C.</option>
                <option value="TI">T.I.</option>
                <option value="RC">Reg. Civil</option>
                <option value="CE">C.E.</option>
                <option value="PA">Pasaporte</option>
              </select>
            </div>
            <div class="col-md-3">
              <input type="text" class="form-control form-control-sm" :class="{'bg-white': acomp.bloqueado}" placeholder="N° Documento" v-model="acomp.numero_documento" :disabled="acomp.bloqueado" required>
            </div>
            <div class="col-md-12">
              <input type="text" class="form-control form-control-sm" :class="{'bg-white': acomp.bloqueado}" placeholder="Parentesco (Ej: Hijo, Esposa)" v-model="acomp.parentesco" :disabled="acomp.bloqueado" required>
            </div>

            <div v-if="acomp.bloqueado" class="col-12 mt-1">
              <small class="text-success"><i class="bi bi-shield-check"></i> Huésped registrado en el sistema</small>
            </div>
          </div>

        </form>
      </div>

      <div class="p-3 bg-light border-top text-end">
        <button type="button" class="btn btn-secondary me-2" @click="cerrar">Cancelar</button>
        <button type="submit" form="formEdicionReserva" class="btn btn-dark px-4" :disabled="guardando">
        <span v-if="guardando" class="spinner-border spinner-border-sm me-2"></span>
        <font-awesome-icon v-else :icon="modoCheckIn ? 'fa-solid fa-check-circle' : 'fa-solid fa-save'" class="me-2" /> 
        {{ modoCheckIn ? 'Confirmar Check-in' : 'Guardar y Continuar' }}
      </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: rgba(15, 59, 42, 0.5); z-index: 1060; backdrop-filter: blur(4px);
}
.modal-box {
  animation: scaleIn 0.3s ease-out forwards; border: 1px solid rgba(15, 59, 42, 0.1);
}
@keyframes scaleIn {
  from { transform: scale(0.9) translateY(20px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}
.hover-danger:hover { color: #dc3545 !important; }
</style>