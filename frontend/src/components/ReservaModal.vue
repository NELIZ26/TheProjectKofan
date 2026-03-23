<script setup>
import { useReservaStore } from "@/stores/reserva";

const store = useReservaStore();

// Ahora simplemente llamamos a la función del store que ya hace todo el trabajo pesado,
// sin meter lógica de WhatsApp aquí.
const handleConfirmarReserva = async () => {
  await store.handleSubmit(); 
};
</script>

<template>
  <div
    class="modal-overlay"
    :class="{ active: store.isModalOpen }"
    @click.self="store.closeModal"
  >
    <div class="modal-card modal-lg"> <button class="btn-close-custom" @click="store.closeModal">
        <font-awesome-icon icon="fa-solid fa-plus" style="transform: rotate(45deg)" />
      </button>

      <div class="modal-body">
        <div class="text-center mb-4">
          <font-awesome-icon icon="fa-solid fa-leaf" class="verde-kofan mb-2 fs-4" />
          <h2 class="fw-bold verde-kofan">Reserva tu Experiencia</h2>
          
          <p v-if="store.habitacionSeleccionada" class="text-muted small mb-0">
            Estás reservando: <strong>{{ store.habitacionSeleccionada.name }}</strong>
          </p>
          <p v-if="store.habitacionSeleccionada" class="text-success fw-bold mt-1">
            Valor por noche: ${{ store.habitacionSeleccionada.price.toLocaleString("es-CO") }} COP
          </p>
          
          <p v-else class="text-muted small">
            Completa tus datos para vivir la magia del Putumayo
          </p>
        </div>

        <div class="tabs-kofan mb-4">
          <button
            type="button"
            class="tab-item"
            :class="{ active: store.personType === 'natural' }"
            @click="store.setPersonType('natural')"
          >
            Persona Natural
          </button>
          <button
            type="button"
            class="tab-item"
            :class="{ active: store.personType === 'juridica' }"
            @click="store.setPersonType('juridica')"
          >
            Empresa (Jurídica)
          </button>
        </div>

        <form @submit.prevent="handleConfirmarReserva" novalidate>
          <div class="row g-3">
            <div class="col-md-8">
              <label class="form-label-kofan">{{ store.labelNombres }}</label>
              <input
                type="text"
                class="input-kofan"
                v-model="store.form.nombres"
                :placeholder="store.placeholderNombres"
                :class="{ 'is-invalid': store.errors.nombres }"
              />
            </div>

            <div class="col-md-4" v-if="store.personType === 'natural'">
              <label class="form-label-kofan">Tipo Documento</label>
              <select
                class="input-kofan"
                v-model="store.form.tipoDocumento"
                :class="{ 'is-invalid': store.errors.tipoDocumento }"
              >
                <option value="" disabled>Seleccione...</option>
                <option value="CC">C.C.</option>
                <option value="CE">C.E.</option>
                <option value="PA">Pasaporte</option>
              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label-kofan">Correo Electrónico</label>
              <input
                type="email"
                class="input-kofan"
                v-model="store.form.correo"
                placeholder="ejemplo@correo.com"
                :class="{ 'is-invalid': store.errors.correo }"
              />
            </div>

            <div class="col-md-6">
              <label class="form-label-kofan">{{ store.labelNumDoc }}</label>
              <input
                type="number"
                class="input-kofan"
                v-model="store.form.numDocumento"
                :class="{ 'is-invalid': store.errors.numDocumento }"
              />
            </div>

            <div class="col-md-4">
              <label class="form-label-kofan">Teléfono</label>
              <input
                type="tel"
                class="input-kofan"
                v-model="store.form.telefono"
                placeholder="300..."
                :class="{ 'is-invalid': store.errors.telefono }"
              />
            </div>

            <div class="col-md-4">
              <label class="form-label-kofan">Huéspedes</label>
              <select class="input-kofan" v-model="store.form.cantidadPersonas">
                <option value="1">1 Persona</option>
                <option value="2">2 Personas</option>
                <option value="3">3 Personas</option>
                <option value="4">4 Personas</option>
                <option value="5+">5+ Personas</option>
              </select>
            </div>

            <div class="col-md-4">
              <label class="form-label-kofan">Alojamiento</label>
              <input
                type="text"
                class="input-kofan bg-light text-muted"
                v-model="store.form.habitacion"
                readonly
                :class="{ 'is-invalid': store.errors.habitacion }"
                title="Alojamiento seleccionado en el catálogo"
              />
            </div>

            <div class="col-md-6">
              <label class="form-label-kofan">Ingreso (Check-In)</label>
              <input
                type="date"
                class="input-kofan"
                v-model="store.form.fechaReserva"
                :min="store.minDate"
                :class="{ 'is-invalid': store.errors.fechaReserva }"
              />
            </div>

            <div class="col-md-6">
              <label class="form-label-kofan">Salida (Check-Out)</label>
              <input
                type="date"
                class="input-kofan"
                v-model="store.form.fechaSalida"
                :min="store.form.fechaReserva || store.minDate"
                :class="{ 'is-invalid': store.errors.fechaSalida }"
              />
            </div>

            <div class="col-12 mt-4" v-if="store.form.cantidadPersonas > 1 || store.form.cantidadPersonas === '5+'">
              <div class="p-3 bg-light rounded border border-light">
                <div class="form-check form-switch d-flex align-items-center mb-0">
                  <input 
                    class="form-check-input me-3" 
                    type="checkbox" 
                    id="switchAcompanantes" 
                    v-model="store.form.registrarAcompanantesAhora"
                    style="transform: scale(1.3); cursor: pointer;"
                  >
                  <label class="form-check-label text-muted small" for="switchAcompanantes" style="cursor: pointer;">
                    <strong style="color: #0f3b2a;">¿Registrar acompañantes ahora?</strong> <br>
                    Puedes hacerlo ahora o dejarnos estos datos en recepción el día de tu llegada.
                  </label>
                </div>

                <div v-if="store.form.registrarAcompanantesAhora" class="mt-4">
                  <div v-for="(acomp, index) in store.form.acompanantes" :key="index" class="row g-2 mb-3 pb-3 border-bottom">
                    <div class="col-12"><strong class="small" style="color: #0f3b2a;">Acompañante {{ index + 1 }}</strong></div>
                    <div class="col-md-4">
                      <input type="text" class="form-control form-control-sm" placeholder="Nombre completo" v-model="acomp.nombre_completo">
                    </div>
                    <div class="col-md-4">
                      <input type="text" class="form-control form-control-sm" placeholder="N° Documento" v-model="acomp.numero_documento">
                    </div>
                    <div class="col-md-4">
                      <input type="text" class="form-control form-control-sm" placeholder="Parentesco (Ej: Hijo)" v-model="acomp.parentesco">
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <div class="text-center mt-5">
            <button type="submit" class="btn-kofan-confirm" :disabled="store.isSubmitting">
            <font-awesome-icon icon="fa-solid fa-check" class="me-2" />
            {{ store.isSubmitting ? 'Procesando...' : 'Confirmar Reserva' }}
          </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Contenedor principal del modal */
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

/* Tarjeta del modal */
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
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-body {
  padding: 3rem;
  max-height: 90vh;
  overflow-y: auto;
}

/* Estilos de las Pestañas (Tabs) */
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

/* Etiquetas y Campos de entrada */
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

/* Estado de error */
.is-invalid {
  border-color: #e74c3c !important;
  background-color: #fff8f8;
}

.verde-kofan {
  color: #0f3b2a;
}

/* Botón de cierre superior */
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

/* Botón Confirmar */
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

/* Responsive */
@media (max-width: 768px) {
  .modal-body {
    padding: 1.5rem;
  }
  .btn-kofan-confirm {
    width: 100%;
  }
}
</style>