<script setup>
import { useReservaStore } from "@/stores/reserva";
import { useAuthStore } from "@/stores/auth"; 
import { DatePicker as VDatePicker } from 'v-calendar'; 
import 'v-calendar/dist/style.css'; 
import { ref, onMounted, onUnmounted, watch } from 'vue'; 

const store = useReservaStore();
const auth = useAuthStore(); 

const columnasCalendario = ref(window.innerWidth >= 768 ? 2 : 1);

const actualizarColumnas = () => {
  columnasCalendario.value = window.innerWidth >= 768 ? 2 : 1;
};

onMounted(() => window.addEventListener('resize', actualizarColumnas));
onUnmounted(() => window.removeEventListener('resize', actualizarColumnas));

watch(() => store.isModalOpen, (isOpen) => {
  if (isOpen && auth.isLogged && auth.user) {
    store.form.nombreCompleto = auth.user.full_name || "";
    store.form.correo = auth.user.email || "";
    store.form.telefono = auth.user.phone || "";
  }
});

const handleConfirmarReserva = async () => {
  await store.handleSubmit(); 
};
</script>

<template>
  <div class="modal-overlay" :class="{ active: store.isModalOpen }" @click.self="store.closeModal">
    <div class="modal-card modal-lg">
      <button class="btn-close-custom" @click="store.closeModal">
        <font-awesome-icon icon="fa-solid fa-plus" style="transform: rotate(45deg)" />
      </button>

      <div class="modal-body pb-2">
        <div class="text-center mb-4">
          <font-awesome-icon icon="fa-solid fa-leaf" class="verde-kofan mb-2 fs-4" />
          <h2 class="fw-bold verde-kofan" v-if="store.habitacionSeleccionada">
            Reservar: <strong>{{ store.habitacionSeleccionada.name }}</strong>
          </h2>
        </div>

        <form @submit.prevent="handleConfirmarReserva" novalidate>
          <div class="row g-3">
            
            <div class="col-12 mb-3 d-flex flex-column align-items-center">
              <label class="form-label-kofan mb-2 text-center fw-bold text-success">1. Selecciona tus fechas</label>
              
              <div class="calendario-wrapper p-2 bg-light rounded border d-flex justify-content-center" style="width: 100%; max-width: 550px;">
                <VDatePicker
                v-model.range="store.selectedDateRange" 
                is-range
                :min-date="store.minDate"
                :disabled-dates="store.disabledDates"
                color="green"
                title-position="left"
                :columns="columnasCalendario"
                :trim-weeks="true" 
              />
              </div>
              
              <p v-if="store.errors.dates" class="text-danger small text-center mt-2 mb-0">Selecciona una fecha de ingreso y salida.</p>
            </div>

            <div v-if="store.totalCalculado > 0" class="col-12 my-3 d-flex justify-content-center animate__animated animate__fadeIn">
              <div class="p-3 rounded-4 shadow-sm position-relative overflow-hidden text-center" style="background-color: #f0fdf4; border: 1px solid #bbf7d0; max-width: 450px; width: 100%;">
                
                <div class="position-absolute top-0 start-0 w-100 py-1 small fw-bold text-white" style="background-color: #198754; opacity: 0.9;">
                  ¡Asegura tu reserva con el 50%!
                </div>

                <div class="mt-4">
                  <p class="mb-0 text-muted fw-medium" style="font-size: 0.85rem;">
                    Total de la estadía: <span class="text-decoration-line-through">{{ store.totalFormateado }}</span>
                  </p>
                  <p class="mb-0 mt-1 text-success fw-bold" style="font-size: 0.9rem;">Transferir ahora:</p>
                  <h3 class="fw-bold mb-1" style="color: #0f3b2a; font-size: 1.8rem;">{{ store.anticipoFormateado }}</h3>
                  <p class="text-muted mb-3" style="font-size: 0.8rem;">Bancolombia Ahorros N° 123-456789-00</p>
                </div>

                <div class="bg-white p-2 rounded-3 border text-start d-flex gap-2 shadow-sm align-items-center" style="border-color: #bbf7d0 !important;">
                  <i class="bi bi-shield-check text-success fs-4"></i>
                  <span style="font-size: 0.75rem; color: #4a4a4a; line-height: 1.3;">
                    <strong>Reserva segura:</strong> Por favor adjunta tu comprobante. Una vez lo envíes, bloquearemos tus fechas y verificaremos el pago para confirmarte.
                  </span>
                </div>

              </div>
            </div>

            <div class="col-12 mt-2">
              <label class="form-label-kofan fw-bold text-success text-center d-block">2. Tus Datos y Comprobante</label>
            </div>

            <div class="col-md-12">
              <label class="form-label-kofan">Nombre y Apellido / Razón Social</label>
              <input type="text" class="input-kofan" v-model="store.form.nombreCompleto" placeholder="Ej: Juan Pérez" :class="{ 'is-invalid': store.errors.nombreCompleto }" />
            </div>

            <div class="col-md-6">
              <label class="form-label-kofan">Celular (WhatsApp)</label>
              <input type="tel" class="input-kofan" v-model="store.form.telefono" placeholder="310 123 4567" :class="{ 'is-invalid': store.errors.telefono }" />
            </div>

            <div class="col-md-6">
              <label class="form-label-kofan">Correo Electrónico</label>
              <input type="email" class="input-kofan" v-model="store.form.correo" placeholder="ejemplo@correo.com" :class="{ 'is-invalid': store.errors.correo }" :disabled="auth.isLogged" />
            </div>

            <div class="col-md-12 mt-3">
              <label class="form-label-kofan text-success fw-bold"><i class="bi bi-camera me-1"></i> Adjuntar Comprobante de Pago</label>
              
              <div v-if="!store.form.comprobantePreview" 
                   class="border border-2 rounded-3 p-4 text-center bg-light transition-all hover-shadow" 
                   style="border-style: dashed !important; border-color: #198754 !important; cursor: pointer;"
                   @dragover.prevent 
                   @drop.prevent="store.handleFileUpload"
                   @click="$refs.fileInput.click()">
                
                <i class="bi bi-cloud-arrow-up fs-1 text-success mb-2"></i>
                <h6 class="mb-1 fw-bold text-dark">Haz clic o arrastra tu comprobante aquí</h6>
                <p class="text-muted small mb-0">Formatos aceptados: JPG, PNG o PDF (Opcional si pagas al llegar)</p>
                
                <input type="file" ref="fileInput" class="d-none" @change="store.handleFileUpload" accept="image/png, image/jpeg, application/pdf" />
              </div>

              <div v-else class="position-relative text-center mt-2 border border-success rounded-3 p-3 bg-white shadow-sm">
                
                <img v-if="store.form.comprobantePreview !== 'pdf-icon'" 
                     :src="store.form.comprobantePreview" 
                     class="img-fluid rounded border shadow-sm" 
                     style="max-height: 180px; object-fit: contain;" />
                
                <div v-else class="py-4">
                  <i class="bi bi-file-earmark-pdf-fill text-danger" style="font-size: 4rem;"></i>
                  <h6 class="mt-2 text-dark">{{ store.form.comprobante.name }}</h6>
                </div>

                <button type="button" 
                        class="btn btn-danger btn-sm position-absolute top-0 end-0 m-2 rounded-circle shadow" 
                        style="width: 35px; height: 35px;"
                        title="Quitar comprobante"
                        @click.stop="store.removerComprobante">
                  <i class="bi bi-trash fs-6"></i>
                </button>
              </div>
              
              <p v-if="store.errors.comprobante" class="text-danger small mt-1">Por favor sube el comprobante de pago.</p>
            </div>

          </div> 

          <div class="text-center mt-5">
            <button type="submit" 
                    class="btn px-4 py-2 rounded-pill shadow-sm transition-all text-white" 
                    style="background-color: #0f3b2a; border: none; font-weight: 500; letter-spacing: 0.5px; font-size: 0.95rem;"
                    :disabled="store.isSubmitting"
                    onmouseover="this.style.opacity='0.85'; this.style.transform='translateY(-1px)'"
                    onmouseout="this.style.opacity='1'; this.style.transform='translateY(0)'">
              <font-awesome-icon icon="fa-solid fa-check" class="me-2 opacity-75" />
              {{ store.isSubmitting ? 'Procesando...' : 'Confirmar y Enviar' }}
            </button>
          </div>
          
          <div class="text-center mt-3 mb-2">
             <a href="https://wa.me/573224225925?text=Hola%20Kof%C3%A1n%2C%20tengo%20una%20duda%20antes%20de%20hacer%20mi%20reserva." 
                target="_blank" 
                class="text-decoration-none" 
                style="color: #1d9e4c; font-weight: 400; font-size: 0.85rem; letter-spacing: 0.3px; transition: opacity 0.2s;"
                onmouseover="this.style.opacity='0.7'"
                onmouseout="this.style.opacity='1'">
               <i class="bi bi-whatsapp align-middle me-1" style="font-size: 1rem; opacity: 0.8;"></i> 
               ¿Tienes dudas? Escríbenos
             </a>
          </div>

        </form>
      </div> 
    </div> 
  </div>
</template>

<style scoped>
/* 🟢 TUS ESTILOS ORIGINALES INTACTOS */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 59, 42, 0.7);
  backdrop-filter: blur(8px);
  display: grid;
  place-items: center;
  z-index: 1050;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.modal-overlay.active {
  opacity: 1;
  visibility: visible;
}

.modal-card {
  background: white;
  width: 95%;
  max-width: 750px;
  border-radius: 25px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-body {
  padding: 3rem;
  max-height: 90vh;
  overflow-y: auto;
}

.tabs-kofan {
  background: #f1f5f2;
  padding: 5px;
  border-radius: 15px;
  display: flex;
}

.tab-item {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px;
  border-radius: 12px;
  font-weight: 700;
  color: #666;
  transition: 0.3s;
}

.tab-item.active {
  background: white;
  color: #0f3b2a;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.form-label-kofan {
  font-size: 0.8rem;
  font-weight: 700;
  color: #0f3b2a;
  margin-bottom: 6px;
  display: block;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-kofan {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fcfcfc;
  transition: all 0.3s ease;
}

.input-kofan:focus {
  outline: none;
  border-color: #2ecc71;
  background: white;
  box-shadow: 0 0 0 4px rgba(46, 204, 113, 0.1);
}

.is-invalid {
  border-color: #e74c3c !important;
  background-color: #fff8f8;
}

.verde-kofan {
  color: #0f3b2a;
}

.btn-close-custom {
  position: absolute;
  top: 20px;
  right: 20px;
  background: #f1f5f2;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: #0f3b2a;
  z-index: 10;
  transition: 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close-custom:hover {
  background: #e74c3c;
  color: white;
  transform: rotate(90deg);
}

.btn-kofan-confirm {
  background: #0f3b2a;
  color: white;
  border: none;
  padding: 16px 60px;
  border-radius: 15px;
  font-weight: 700;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 10px 15px -3px rgba(15, 59, 42, 0.3);
}

.btn-kofan-confirm:hover {
  background: #1a5c43;
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(15, 59, 42, 0.4);
}

/* 🟢 NUEVOS ESTILOS PARA EL CALENDARIO */
.calendario-wrapper {
  overflow: hidden; 
}
.calendario-wrapper :deep(.vc-expanded) {
  width: 100% !important;
}
.calendario-wrapper :deep(.vc-container) {
  border: none !important;
  background-color: transparent !important;
}
.calendario-wrapper :deep(.vc-day-content.vc-disabled) {
  opacity: 0.4 !important;
  text-decoration: line-through; 
  color: #e74c3c; /* Las fechas ocupadas se verán rojizas */
}

@media (max-width: 768px) {
  .modal-body {
    padding: 1.5rem;
  }
  .btn-kofan-confirm {
    width: 100%;
  }
}
.calendario-wrapper :deep(.vc-container) {
  margin-left: auto !important;
  margin-right: auto !important;
  max-width: 600px !important; 
}

.vc-day.is-not-in-month,
.vc-day.in-prev-month,
.vc-day.in-next-month {
  opacity: 0 !important;
  pointer-events: none !important;
  visibility: hidden !important;
}

/* Evita que los fondos rojos/verdes se salgan de sus casillas */
.vc-highlight {
  overflow: hidden !important;
}
</style>