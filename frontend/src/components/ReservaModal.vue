<script setup>
import { useReservaStore } from "@/stores/reserva";
import { DatePicker as VDatePicker } from 'v-calendar'; 
import 'v-calendar/dist/style.css'; 
import { ref, onMounted, onUnmounted } from 'vue'; // 🟢 Agregamos esto

const store = useReservaStore();

// 🟢 Lógica para saber si mostrar 1 o 2 calendarios según la pantalla
const columnasCalendario = ref(window.innerWidth >= 768 ? 2 : 1);

const actualizarColumnas = () => {
  columnasCalendario.value = window.innerWidth >= 768 ? 2 : 1;
};

// Escuchamos si el cliente voltea el celular o cambia el tamaño de la ventana
onMounted(() => window.addEventListener('resize', actualizarColumnas));
onUnmounted(() => window.removeEventListener('resize', actualizarColumnas));

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

      <div class="modal-body">
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
                />
              </div>
              
              <p v-if="store.errors.dates" class="text-danger small text-center mt-2 mb-0">Selecciona una fecha de ingreso y salida.</p>
            </div>

            <div class="col-12 mt-3">
              <label class="form-label-kofan fw-bold text-success text-center d-block">2. Datos de Contacto</label>
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
              <input type="email" class="input-kofan" v-model="store.form.correo" placeholder="ejemplo@correo.com" :class="{ 'is-invalid': store.errors.correo }" />
            </div>

          </div> 

          <div class="text-center mt-5">
            <button type="submit" class="btn-kofan-confirm" :disabled="store.isSubmitting">
              <font-awesome-icon icon="fa-solid fa-check" class="me-2" />
              {{ store.isSubmitting ? 'Procesando...' : 'Solicitar Reserva' }}
            </button>
          </div>
        </form>
        
      </div> </div> </div> </template>

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
</style>