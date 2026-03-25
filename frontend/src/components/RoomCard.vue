<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  habitacion: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['reservar']);
const API_BASE_URL = "http://127.0.0.1:8000";

const indiceFotoActiva = ref(0);

const imagenes = computed(() => {
  if (props.habitacion.images && props.habitacion.images.length > 0) {
    return props.habitacion.images.slice(0, 5).map(img => `${API_BASE_URL}${img}`);
  }
  if (props.habitacion.main_image) {
    return [`${API_BASE_URL}${props.habitacion.main_image}`];
  }
  return ['https://via.placeholder.com/800x500?text=Kofan+Hospedaje'];
});

const fotoPrincipal = computed(() => imagenes.value[indiceFotoActiva.value]);

const mapaIconos = {
  "Aire Acondicionado": "bi bi-snow2",
  "Ventilador": "bi bi-fan",
  "Televisión": "bi bi-tv",
  "Wifi": "bi bi-wifi",
  "Baño Privado": "bi bi-droplet",
  "Nevera / Minibar": "bi bi-cup-straw",
  "Zonas Verdes": "bi bi-tree",
  "Vista a la Selva": "bi bi-binoculars",
  "Malla Catamarán": "bi bi-grid-3x3",
  "Tina / Jacuzzi": "bi bi-water",
  "Balcón": "bi bi-house-door"
};

const formatPrice = (v) => {
  return (v || 0).toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });
};

const handleReservar = () => {
  emit('reservar', props.habitacion);
};

// 🟢 Funciones para el deslizador de fotos
const siguienteFoto = () => {
  if (imagenes.value.length > 1) {
    indiceFotoActiva.value = (indiceFotoActiva.value + 1) % imagenes.value.length;
  }
};

const anteriorFoto = () => {
  if (imagenes.value.length > 1) {
    indiceFotoActiva.value = (indiceFotoActiva.value - 1 + imagenes.value.length) % imagenes.value.length;
  }
};
</script>

<template>
  <div class="card habitacion-premium shadow-lg border-0 rounded-4 overflow-hidden mb-5">
    <div class="row g-0 align-items-stretch">
      
      <div class="col-lg-7 p-0 position-relative galeria-wrapper">
        <div class="position-absolute w-100 h-100 top-0 start-0 overflow-hidden z-0 bg-dark">
          <img :src="fotoPrincipal" class="foto-principal w-100 h-100" :alt="habitacion.name">
        </div>
        
        <div class="position-absolute top-0 start-0 m-3 d-flex gap-2 z-1">
          <span class="badge bg-success bg-opacity-75 rounded-pill px-3 py-2 shadow-sm">
            <i class="bi bi-people-fill me-1"></i> Hasta {{ habitacion.capacity }} pers.
          </span>
        </div>

        <button v-if="imagenes.length > 1" @click.stop="anteriorFoto" class="btn-slider btn-slider-prev position-absolute top-50 start-0 translate-middle-y ms-3 z-1 shadow">
          <i class="bi bi-chevron-left"></i>
        </button>
        
        <button v-if="imagenes.length > 1" @click.stop="siguienteFoto" class="btn-slider btn-slider-next position-absolute top-50 end-0 translate-middle-y me-3 z-1 shadow">
          <i class="bi bi-chevron-right"></i>
        </button>
      </div>

      <div class="col-lg-5">
        <div class="card-body p-4 p-xl-5 h-100 d-flex flex-column z-1 position-relative bg-white">
          
          <div class="encabezado mb-3 pb-3 border-bottom border-light">
            <h2 class="titulo-habitacion fw-bold mb-2">{{ habitacion.name }}</h2>
            <p class="text-muted mb-0 descripcion-corta">{{ habitacion.description }}</p>
          </div>

          <div v-if="imagenes.length > 1" class="galeria-derecha mb-4">
            <div class="d-flex gap-2 flex-wrap mt-2">
              <div v-for="(img, index) in imagenes" :key="index" 
                   @click="indiceFotoActiva = index"
                   class="miniatura-derecha rounded-3 overflow-hidden shadow-sm border border-2" 
                   :class="index === indiceFotoActiva ? 'border-success' : 'border-transparent'">
                <img :src="img" class="img-fluid w-100 h-100" alt="Vista miniatura">
              </div>
            </div>
          </div>

          <div class="detalles-tecnicos mb-4 flex-grow-1">
            <h6 class="text-uppercase text-muted fw-bold small mb-3 tracking-wider">¿Qué incluye?</h6>
            <div class="row g-3">
              
              <template v-if="habitacion.amenities && habitacion.amenities.length > 0">
                <div v-for="(amenidad, index) in habitacion.amenities" :key="index" class="col-6 d-flex align-items-center">
                  <i :class="[mapaIconos[amenidad] || 'bi bi-check2-circle']" class="text-success fs-4 me-3 p-2 bg-success bg-opacity-10 rounded-circle"></i>
                  <div>
                    <strong class="text-dark small d-block" style="line-height: 1.2;">{{ amenidad }}</strong>
                  </div>
                </div>
              </template>

              <template v-else>
                <div class="col-12">
                  <small class="text-muted fst-italic">Detalles básicos incluidos. Consulta en recepción.</small>
                </div>
              </template>

            </div>
          </div>

          <div class="seccion-precio-accion bg-light rounded-4 p-3 text-dark mt-auto border">
            <div class="row align-items-center">
              <div class="col-sm-6 text-center text-sm-start mb-3 mb-sm-0">
                <p class="mb-0 text-success fw-bold small">Precio por noche</p>
                <p class="mb-0 h2 fw-bold" style="color: #0f3b2a;">{{ formatPrice(habitacion.price) }}</p>
              </div>
              <div class="col-sm-6 text-center text-sm-end">
                <button @click="handleReservar" class="btn-reservar-premium w-100 rounded-pill">
                  Reservar <i class="bi bi-arrow-right ms-2 icono-flecha"></i>
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.habitacion-premium { 
  transition: transform 0.3s ease; 
}
.habitacion-premium:hover { 
  transform: translateY(-5px); 
}

.titulo-habitacion {
  font-size: 2.3rem; 
  color: #0f3b2a; 
  letter-spacing: -0.5px; 
  line-height: 1.1;
}

.galeria-wrapper { 
  min-height: 380px; 
}
.foto-principal { 
  object-fit: cover; 
  transition: opacity 0.3s ease; 
}

.btn-slider {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background-color: rgba(255, 255, 255, 0.7);
  color: #0f3b2a;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(4px);
}
.btn-slider:hover {
  background-color: #ffffff;
  transform: translateY(-50%) scale(1.1);
  color: #2ecc71;
}

/* Miniaturas ajustadas para verse más elegantes */
.miniatura-derecha {
  width: 70px;
  height: 50px;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.3s ease, opacity 0.3s;
}
.miniatura-derecha img {
  object-fit: cover;
}
.miniatura-derecha:hover {
  transform: translateY(-3px);
  opacity: 1 !important;
}
.border-transparent { 
  border-color: transparent !important; 
  opacity: 0.6; /* Un poco más tenues para resaltar la seleccionada */
}
.border-success {
  border-color: #2ecc71 !important;
  opacity: 1;
}

.descripcion-corta { font-size: 1.05rem; line-height: 1.5; color: #555 !important; }

/* 🟢 ESTILOS DEL NUEVO BOTÓN PREMIUM */
.btn-reservar-premium {
  background-color: #0f3b2a;
  color: #ffffff;
  border: none;
  padding: 0.8rem 1.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(15, 59, 42, 0.2); /* Sombra suave */
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.btn-reservar-premium:hover {
  background-color: #16523b; /* Un verde sutilmente más claro al pasar el mouse */
  color: #ffffff;
  transform: translateY(-2px); /* Se levanta un poco */
  box-shadow: 0 8px 20px rgba(15, 59, 42, 0.3); /* Sombra más pronunciada */
}
.icono-flecha {
  transition: transform 0.3s ease;
}
.btn-reservar-premium:hover .icono-flecha {
  transform: translateX(5px); /* La flecha se desliza a la derecha */
}

@media (max-width: 991.98px) {
  .galeria-wrapper { min-height: 300px; }
  .titulo-habitacion { font-size: 1.8rem; }
}
</style>