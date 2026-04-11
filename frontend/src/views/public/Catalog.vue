<template>
  <div id="contenido1" class="bg-light-kofan">
    <div class="header-section text-center py-5">
      <font-awesome-icon icon="fa-solid fa-mountain-sun" class="verde-kofan mb-3 fs-1" />
      <h1 class="fw-bold verde-kofan">Nuestros Alojamientos</h1>
      <p class="text-muted container" style="max-width: 700px">
        Desconéctate del mundo y reconéctate con la tierra. Elige entre la privacidad de nuestras cabañas
        artesanales o la calidez de nuestras habitaciones tradicionales.
      </p>
    </div>

    <div v-if="loading" class="container pb-5">
      <div class="empty-state">
        Cargando alojamientos disponibles...
      </div>
    </div>

    <div v-else-if="errorMessage" class="container pb-5">
      <div class="empty-state empty-state--warning">
        <p class="mb-3">{{ errorMessage }}</p>
        <button class="btn btn-kofan px-4" @click="cargarCatalogo">Reintentar</button>
      </div>
    </div>

    <div v-else-if="!hayResultados" class="container pb-5">
      <div class="empty-state">
        Aún no hay alojamientos disponibles para mostrar.
      </div>
    </div>

    <template v-else>
      <section v-if="cabanasIndependientes.length > 0" class="container mb-5" id="seccionCabanas">
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

      <section v-if="habitacionesFamiliares.length > 0" class="container mb-5" id="seccionFamiliares">
        <div class="d-flex align-items-center mb-4">
          <div class="linea-verde"></div>
          <h2 class="mx-3 fw-bold verde-kofan">Habitaciones Familiares</h2>
        </div>

        <RoomCard
          v-for="h in habitacionesFamiliares"
          :key="h.id || h._id"
          :habitacion="h"
          @reservar="reserva.openModal($event)"
        />
      </section>

      <section v-if="habitacionesIndividuales.length > 0" class="container pb-5" id="seccionIndividuales">
        <div class="d-flex align-items-center mb-4">
          <div class="linea-verde"></div>
          <h2 class="mx-3 fw-bold verde-kofan">Habitaciones Individuales</h2>
        </div>

        <RoomCard
          v-for="h in habitacionesIndividuales"
          :key="h.id || h._id"
          :habitacion="h"
          @reservar="reserva.openModal($event)"
        />
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useReservaStore } from "@/stores/reserva.js";
import { getRooms } from "@/services/roomService";
import RoomCard from "@/components/RoomCard.vue";

const reserva = useReservaStore();
const allAccommodations = ref([]);
const loading = ref(false);
const errorMessage = ref("");

const obtenerListaHabitaciones = (response) => {
  if (Array.isArray(response?.data)) return response.data;
  if (Array.isArray(response)) return response;
  return [];
};

const obtenerEstadoActivo = (habitacion) => {
  const valor = habitacion?.active;

  if (valor === undefined || valor === null) return true;
  if (typeof valor === "string") return valor.toLowerCase() !== "false";

  return valor !== false;
};

const normalizarTipoAlojamiento = (type = "") => {
  const tipo = String(type)
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();

  if (!tipo) return "individual";

  if (["cabana", "cabanas", "cabin", "cabins"].includes(tipo) || tipo.includes("cab")) {
    return "cabana";
  }

  if (["family", "familiar", "familiares"].includes(tipo) || tipo.includes("fam")) {
    return "familiar";
  }

  if (["habitacion", "habitaciones", "individual", "single", "suite", "room", "rooms"].includes(tipo)) {
    return "individual";
  }

  return "individual";
};

const cargarCatalogo = async () => {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await getRooms();
    allAccommodations.value = obtenerListaHabitaciones(response);
  } catch (error) {
    console.error("Error al cargar los alojamientos:", error);
    errorMessage.value = "No fue posible cargar el catálogo en este momento.";
    allAccommodations.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  cargarCatalogo();
});

const alojamientosActivos = computed(() =>
  allAccommodations.value.filter((acomodacion) => obtenerEstadoActivo(acomodacion))
);

const filtrarPorTipo = (tipoEsperado) =>
  alojamientosActivos.value.filter(
    (acomodacion) => normalizarTipoAlojamiento(acomodacion?.type) === tipoEsperado
  );

const cabanasIndependientes = computed(() => filtrarPorTipo("cabana"));
const habitacionesFamiliares = computed(() => filtrarPorTipo("familiar"));
const habitacionesIndividuales = computed(() => filtrarPorTipo("individual"));

const hayResultados = computed(
  () =>
    cabanasIndependientes.value.length +
      habitacionesFamiliares.value.length +
      habitacionesIndividuales.value.length >
    0
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

.empty-state {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--k-border, #e1d7cc);
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(15, 59, 42, 0.08);
  color: var(--k-muted, #5f6f65);
  padding: 2rem;
  text-align: center;
}

.empty-state--warning {
  color: var(--k-forest);
}
</style>