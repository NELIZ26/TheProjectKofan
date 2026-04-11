<template>
  <div class="service-selection">
    <div class="overlay-kofan">
      <div class="container text-center py-5">
        <font-awesome-icon
          icon="fa-solid fa-leaf"
          class="leaf-icon mb-3 fs-1"
        />
        <h1 class="display-4 fw-bold text-white mb-2 title-kofan">Experiencias Kofán</h1>
        <p class="text-light lead mb-5 subtitle-kofan">
          Elige el tipo de experiencia que deseas vivir en el corazón del Putumayo
        </p>

        <div class="row g-4 justify-content-center">
          <div class="col-md-5">
            <div class="card-selection shadow-lg" @click="goToHospedaje">
              <div class="card-image hospedaje-bg"></div>
              <div class="card-content">
                <h2 class="fw-bold">Hospedaje</h2>
                <p>
                  Cabañas privadas y habitaciones diseñadas para el descanso
                  profundo y la conexión con la naturaleza.
                </p>
                <button class="btn btn-kofan rounded-pill px-4">
                  Explorar Cabañas
                </button>
              </div>
            </div>
          </div>

          <div class="col-md-5">
            <div class="card-selection shadow-lg inactive-card">
              <div class="card-image eventos-bg"></div>
              <div class="card-content">
                <h2 class="fw-bold">Eventos y Bodas</h2>
                <p>
                  Celebra tus momentos especiales rodeado de la magia ancestral
                  y paisajes inolvidables.
                </p>
                <span class="badge bg-warning text-dark badge-kofan">Próximamente</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

// Cambiamos la ruta para que coincida con la que tenías (rooms)
const goToHospedaje = () => {
  router.push({ name: 'rooms' });
};
</script>

<style scoped>
/* ELIMINADO el margin-top para que empiece desde arriba del todo */
.service-selection {
  min-height: 100vh;
  background-image: url("https://i0.wp.com/www.lasillavacia.com/wp-content/uploads/2023/10/LaPaya_Portada.jpg?fit=1200%2C700&ssl=1");
  background-size: cover;
  background-position: center;
}

.overlay-kofan {
  min-height: 100vh;
  background: rgba(15, 59, 42, 0.85); /* Verde oscuro corporativo con opacidad */
  display: flex;
  align-items: center;
}

.title-kofan {
  font-family: 'Forum', serif;
}

.subtitle-kofan, .card-content p {
  font-family: 'Forum', serif;
}

.leaf-icon {
  color: var(--k-apple);
}

.card-selection {
  background: var(--k-cream);
  border-radius: 25px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  height: 100%;
  border: 1px solid var(--k-border);
}

.card-selection:hover {
  transform: translateY(-15px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
}

.card-image {
  height: 250px;
  background-size: cover;
  background-position: center;
}

.hospedaje-bg {
  background-image: url("@/img/habitacion2.jpg");
}
.eventos-bg {
  background-image: url("@/img/eventos3.jpg");
}

.card-content {
  padding: 2.5rem;
  text-align: center;
}

.card-content h2 {
  font-family: 'Forum', serif;
  color: var(--k-forest);
}

.btn-kofan {
  background-color: var(--k-forest);
  color: var(--k-cream);
  font-family: 'Handlee', cursive;
  border: none;
  transition: background 0.3s;
}

.btn-kofan:hover {
  background-color: var(--k-apple);
  color: var(--k-forest);
}

.badge-kofan {
  font-family: 'Handlee', cursive;
}

.inactive-card {
  filter: grayscale(1);
  opacity: 0.7;
  cursor: not-allowed;
}

.inactive-card:hover {
  transform: none;
}
</style>