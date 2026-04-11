<template>
  <div id="contenido1" class="bg-light-kofan">
    
    <div class="header-section text-center py-5">
      <font-awesome-icon icon="fa-solid fa-mountain-sun" class="verde-kofan mb-3 fs-1" />
      <h1 class="fw-bold verde-kofan">Nuestros Alojamientos</h1>
      <p class="text-muted container" style="max-width: 700px">
        Desconéctate del mundo y reconéctate con la tierra. Elige entre la privacidad de nuestras cabañas artesanales o la calidez de nuestras habitaciones tradicionales.
      </p>
    </div>

    <section class="container mb-5" id="seccionCabanas">
      <div class="d-flex align-items-center mb-4">
        <div class="linea-verde"></div>
        <h2 class="mx-3 fw-bold verde-kofan">Cabañas Independientes</h2>
      </div>

      <RoomCard 
        v-for="c in cabanasIndependientes" 
        :key="c.id || c._id" 
        :habitacion="c" 
        @reservar="reserva.openModal($event)" 
      />

      <div v-if="cabanasIndependientes.length === 0" class="text-center py-4 text-muted rounded-4 bg-white shadow-sm border">
        Aún no hay cabañas visibles en esta categoría.
      </div>
    </section>

    <section class="container pb-5" id="seccionHabitaciones">
      <div class="d-flex align-items-center mb-4">
        <div class="linea-verde"></div>
        <h2 class="mx-3 fw-bold verde-kofan">Habitaciones en Maloka</h2>
      </div>

      <RoomCard 
        v-for="h in habitacionesMaloka" 
        :key="h.id || h._id" 
        :habitacion="h" 
        @reservar="reserva.openModal($event)" 
      />

      <div v-if="habitacionesMaloka.length === 0" class="text-center py-4 text-muted rounded-4 bg-white shadow-sm border">
        Aún no hay habitaciones visibles en esta categoría.
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useReservaStore } from "@/stores/reserva.js";
import { getRooms } from "@/services/roomService"; 

// 🟢 Importamos la nueva tarjeta de diseño premium
import RoomCard from "@/components/RoomCard.vue"; 

const reserva = useReservaStore();
const allAccommodations = ref([]);

const cargarCatalogo = async () => {
  try {
    const response = await getRooms();
    allAccommodations.value = response?.data && Array.isArray(response.data) ? response.data : 
                              Array.isArray(response) ? response : [];
  } catch (error) {
    console.error("Error al cargar los alojamientos:", error);
  }
};

onMounted(() => {
  cargarCatalogo();
});

const normalizarTipoAlojamiento = (type = "") => {
  const tipo = String(type)
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();

  if (["cabana", "cabanas", "cabin", "cabins"].includes(tipo) || tipo.includes("cab")) {
    return "cabana";
  }

  if (["habitacion", "habitaciones", "individual", "family", "suite", "room", "rooms"].includes(tipo)) {
    return "habitacion";
  }

  return "habitacion";
};

const alojamientosActivos = computed(() =>
  allAccommodations.value.filter((a) => a.active !== false)
);

const cabanasIndependientes = computed(() =>
  alojamientosActivos.value.filter((a) => normalizarTipoAlojamiento(a.type) === "cabana")
);

const habitacionesMaloka = computed(() =>
  alojamientosActivos.value.filter((a) => normalizarTipoAlojamiento(a.type) === "habitacion")
);
</script>

<style scoped>
.bg-light-kofan {
  background-color: rgba(139, 207, 91, 0.06);
  min-height: 100vh;
  margin-top: 60px;
}
.verde-kofan {
  color: var(--k-forest);
}
.linea-verde {
  height: 4px;
  width: 50px;
  background-color: var(--k-apple);
  border-radius: 2px;
}
</style>