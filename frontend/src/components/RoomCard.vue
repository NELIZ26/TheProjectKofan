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
const mostrarLightbox = ref(false); 

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

const amenidadesSeguras = computed(() => props.habitacion.amenities || []);

const formatPrice = (v) => {
  return (v || 0).toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });
};

const handleReservar = () => { emit('reservar', props.habitacion); };

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

const abrirLightbox = () => { mostrarLightbox.value = true; };
const cerrarLightbox = () => { mostrarLightbox.value = false; };
</script>

<template>
  <div>
    
    <div class="card habitacion-premium shadow-lg border-0 rounded-4 overflow-hidden mb-5">
      <div class="row g-0 align-items-stretch">
        
        <div class="col-lg-5 p-0 position-relative galeria-wrapper overflow-hidden">
          <div class="position-absolute w-100 h-100 top-0 start-0 z-0 bg-dark pointer-cursor" @click="abrirLightbox">
            <img :src="fotoPrincipal" class="foto-principal w-100 h-100" :alt="habitacion.name">
          </div>
          
          <div class="position-absolute top-0 start-0 m-3 d-flex gap-2 z-1">
            <span class="badge bg-success bg-opacity-75 rounded-pill px-3 py-2 shadow-sm fs-badge">
               Hasta {{ habitacion.capacity }} pers.
            </span>
          </div>

          <button v-if="imagenes.length > 1" @click.stop="anteriorFoto" class="btn-desplazador-fino position-absolute top-50 start-0 translate-middle-y ms-3 z-1">
            <i class="bi bi-arrow-left-short fs-2"></i>
          </button>
          
          <button v-if="imagenes.length > 1" @click.stop="siguienteFoto" class="btn-desplazador-fino position-absolute top-50 end-0 translate-middle-y me-3 z-1">
            <i class="bi bi-arrow-right-short fs-2"></i>
          </button>

          <div class="position-absolute bottom-0 end-0 m-3 z-1 lupa-icono pointer-cursor" @click="abrirLightbox">
            <i class="bi bi-search fs-5 lupa-tono-suave"></i>
          </div>
        </div>

        <div class="col-lg-7">
          <div class="card-body p-4 p-xl-5 h-100 d-flex flex-column z-1 position-relative bg-white">
            
            <div class="encabezado mb-3 pb-3 border-bottom border-light">
              <h2 class="titulo-habitacion fw-bold mb-2">{{ habitacion.name }}</h2>
              <p class="text-muted mb-1 descripcion-corta text-truncate-2">{{ habitacion.description }}</p>
              
              <div v-if="habitacion.num_cuartos || habitacion.tipo_camas" class="info-distribucion mt-2 d-flex align-items-center flex-wrap text-muted" style="font-size: 0.9rem;">
                <span v-if="habitacion.num_cuartos" class="d-flex align-items-center">
                  <i class="bi bi-door-open text-success opacity-75 me-1 fs-6"></i> 
                  <span class="fw-medium">{{ habitacion.num_cuartos }} Hab.</span>
                </span>
                <span v-if="habitacion.num_cuartos && habitacion.tipo_camas" class="mx-2 opacity-50">•</span>
                <span v-if="habitacion.tipo_camas" class="d-flex align-items-center">
                  <i class="bi bi-moon-stars text-success opacity-75 me-1"></i> 
                  <span>{{ habitacion.tipo_camas }}</span>
                </span>
              </div>
            </div>

            <div class="amenidades-minimalistas mb-4 flex-grow-1">
              <div class="row row-cols-2 row-cols-md-3 g-3">
                <template v-if="amenidadesSeguras.length > 0">
                  <div v-for="(amenidad, index) in amenidadesSeguras" :key="index" class="col amenidad-item">
                    <i :class="[mapaIconos[amenidad] || 'bi bi-check']" class="icono-fino"></i>
                    <span class="small">{{ amenidad }}</span>
                  </div>
                </template>
                <template v-else>
                  <div class="col-12 text-muted fst-italic small">Detalles básicos incluidos. Consulta en recepción.</div>
                </template>
              </div>
            </div>

            <div class="mt-auto pt-4 border-top border-light d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-3">
              <div class="precio-bloque">
                <p class="mb-0 text-muted fw-bold small text-uppercase" style="letter-spacing: 1px;">Desde</p>
                <div class="d-flex align-items-baseline gap-2">
                  <span class="h2 fw-bold mb-0" style="color: #0f3b2a;">{{ formatPrice(habitacion.price) }}</span>
                  <span class="text-muted small">/ noche</span>
                </div>
              </div>
              <div>
                <button @click="handleReservar" class="btn btn-reservar-pequeno">
                  Reservar <i class="bi bi-arrow-right ms-1 icono-flecha"></i>
                </button>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>

    <div v-if="mostrarLightbox" class="lightbox-overlay" @click="cerrarLightbox">
      <div class="lightbox-content position-relative" @click.stop>
        <img :src="fotoPrincipal" class="img-fluid rounded lightbox-image shadow-lg">
        
        <button v-if="imagenes.length > 1" @click="anteriorFoto" class="btn-lightbox-nav btn-lightbox-prev position-absolute top-50 start-0 translate-middle-y ms-3">
          <i class="bi bi-chevron-left fs-2 text-white"></i>
        </button>
        <button v-if="imagenes.length > 1" @click="siguienteFoto" class="btn-lightbox-nav btn-lightbox-next position-absolute top-50 end-0 translate-middle-y me-3">
          <i class="bi bi-chevron-right fs-2 text-white"></i>
        </button>

        <button @click="cerrarLightbox" class="position-absolute top-0 end-0 m-3 btn-close-lightbox border-0 bg-transparent">
          <i class="bi bi-x-lg fs-4 text-white p-2 rounded-circle bg-dark bg-opacity-25 shadow"></i>
        </button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.habitacion-premium { transition: transform 0.3s ease; }
.habitacion-premium:hover { transform: translateY(-5px); }

.titulo-habitacion { font-size: 2.1rem; color: #0f3b2a; letter-spacing: -0.5px; line-height: 1.1; }

.fs-badge { font-size: 0.85rem; font-weight: 500; }

.galeria-wrapper { min-height: 280px; }
.foto-principal { object-fit: cover; transition: opacity 0.3s ease; }

/* 🟢 NUEVOS ESTILOS PARA LOS DESPLAZADORES (SOLO ICONO Y MÁS GRANDES) */
.btn-desplazador-fino {
  border: none;
  background-color: transparent; /* Sin contenedor */
  color: #f1f1f1; /* Tono hueso suave (off-white) */
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0.7; /* Sutil por defecto */
}
.btn-desplazador-fino:hover {
  color: #ffffff; /* Blanco puro en hover */
  transform: translateY(-50%) scale(1.1); /* Sutil crecimiento */
  opacity: 1;
}

/* 🟢 NUEVOS ESTILOS PARA LA LUPA (SOLO ICONO) */
.lupa-icono i {
  transition: all 0.3s ease;
  padding: 5px; /* Sutil padding para área de clic */
}
.lupa-icono:hover i {
  transform: scale(1.1);
}
.lupa-tono-suave {
  color: #e0e0e0; /* Tono integrado súper suave */
}

.amenidades-minimalistas { font-size: 0.95rem; color: #555; }
.amenidad-item { display: flex; align-items: center; }
.icono-fino { color: #2ecc71; margin-right: 8px; font-size: 1.1rem; }

.descripcion-corta { font-size: 1.0rem; line-height: 1.4; color: #666 !important; }
.text-truncate-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* Botón Premium Pequeño y Cuadrado Suave */
.btn-reservar-pequeno {
  background-color: #114232; 
  color: #ffffff;
  border: none;
  padding: 0.6rem 1.4rem; 
  font-size: 1rem;
  font-weight: 500;
  border-radius: 8px; /* Cuadrado con bordes suaves */
  transition: all 0.3s ease;
}
.btn-reservar-pequeno:hover {
  background-color: #1a5c46; 
  color: #ffffff;
  transform: translateY(-2px); 
  box-shadow: 0 4px 12px rgba(17, 66, 50, 0.3); 
}
.icono-flecha { transition: transform 0.3s ease; }
.btn-reservar-pequeno:hover .icono-flecha { transform: translateX(4px); }

.pointer-cursor { cursor: pointer; }

/* LIGHTBOX (Sin cambios) */
.lightbox-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.9); display: flex; justify-content: center; align-items: center; z-index: 9999; }
.lightbox-content { max-width: 90vw; max-height: 90vh; }
.lightbox-image { max-width: 100%; max-height: 100vh; object-fit: contain; }
.btn-lightbox-nav { border: none; background-color: transparent; cursor: pointer; transition: transform 0.2s ease; }
.btn-lightbox-nav:hover { transform: scale(1.1); }
.btn-close-lightbox { opacity: 0.7; transition: opacity 0.2s ease; }
.btn-close-lightbox:hover { opacity: 1; }

@media (max-width: 991.98px) {
  .galeria-wrapper { min-height: 250px; }
  .titulo-habitacion { font-size: 1.6rem; }
}
</style>