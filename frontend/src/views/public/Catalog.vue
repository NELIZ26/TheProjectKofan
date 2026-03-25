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

const cabanasIndependientes = computed(() =>
  allAccommodations.value.filter((a) => a.type === "cabana" && a.active === true)
);

const habitacionesMaloka = computed(() =>
  allAccommodations.value.filter((a) => a.type === "habitacion" && a.active === true)
);
</script>

<style scoped>
.bg-light-kofan {
  background-color: #f8fcf9;
  min-height: 100vh;
  margin-top: 60px;
}
.verde-kofan {
  color: #0f3b2a;
}
.linea-verde {
  height: 4px;
  width: 50px;
  background-color: #2ecc71;
  border-radius: 2px;
}
</style>