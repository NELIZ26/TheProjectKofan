<template>
  <main class="contacto-page">
    <!-- Hero -->
    <section
      class="contacto-hero text-center text-white d-flex align-items-center"
    >
      <div class="container">
        <h1 class="titulo-contacto">Estamos para escucharte</h1>
        <p class="lead">
          ¿Tienes dudas? Déjanos un mensaje y te responderemos con el alma
          amazónica.
        </p>
      </div>
    </section>

    <!-- Redes + Info + Formulario -->
    <section class="info-formulario py-5">
      <div class="container">
        <div class="row g-5 align-items-stretch">
          <!-- COLUMNA IZQUIERDA: Redes sociales -->
          <div class="col-lg-4 d-flex">
            <div class="card-redes p-4 w-100">
              <h2 class="mb-2">Síguenos</h2>
              <p class="text-white-50 small mb-4">
                Encuéntranos en nuestras redes y mantente al tanto de todo lo
                que pasa en Kofán.
              </p>

              <div class="red-item mb-4">
                <a
                  href="https://www.instagram.com/ecohotelkofan/"
                  target="_blank"
                  class="red-link d-flex align-items-center gap-3"
                >
                  <div class="red-icon-box instagram">
                    <font-awesome-icon :icon="['fab', 'instagram']" />
                  </div>
                  <div>
                    <h6 class="mb-0 text-white fw-bold">Instagram</h6>
                    <p class="mb-0 text-white-50 small">@ecohotelkofan</p>
                  </div>
                </a>
              </div>

              <div class="red-item mb-4">
                <a
                  href="https://www.tiktok.com/@ecohotelkofan"
                  target="_blank"
                  class="red-link d-flex align-items-center gap-3"
                >
                  <div class="red-icon-box tiktok">
                    <font-awesome-icon :icon="['fab', 'tiktok']" />
                  </div>
                  <div>
                    <h6 class="mb-0 text-white fw-bold">TikTok</h6>
                    <p class="mb-0 text-white-50 small">@ecohotelkofan</p>
                  </div>
                </a>
              </div>

              <div class="red-item mb-4">
                <a
                  href="https://wa.link/gjt05p"
                  target="_blank"
                  class="red-link d-flex align-items-center gap-3"
                >
                  <div class="red-icon-box whatsapp">
                    <font-awesome-icon :icon="['fab', 'whatsapp']" />
                  </div>
                  <div>
                    <h6 class="mb-0 text-white fw-bold">WhatsApp</h6>
                    <p class="mb-0 text-white-50 small">+57 322 4225925</p>
                  </div>
                </a>
              </div>

              <div class="red-item mb-2">
                <a
                  href="https://www.facebook.com/ecohotelkofan"
                  target="_blank"
                  class="red-link d-flex align-items-center gap-3"
                >
                  <div class="red-icon-box facebook">
                    <font-awesome-icon :icon="['fab', 'facebook-f']" />
                  </div>
                  <div>
                    <h6 class="mb-0 text-white fw-bold">Facebook</h6>
                    <p class="mb-0 text-white-50 small">Ecohotel Kofán</p>
                  </div>
                </a>
              </div>
            </div>
          </div>

          <!-- COLUMNA DERECHA: Info de contacto + Formulario -->
          <div class="col-lg-8 d-flex flex-column">
            <!-- Info de contacto -->
            <div class="card-info-contacto p-4 mb-4">
              <h2 class="mb-4">Información de Contacto</h2>
              <div class="row g-3">
                <div class="col-md-4">
                  <div class="dato-item d-flex align-items-start gap-3">
                    <div class="icon-box flex-shrink-0">
                      <font-awesome-icon :icon="['fas', 'location-dot']" />
                    </div>
                    <div>
                      <h6 class="mb-0">Ubicación</h6>
                      <p class="mb-0 text-muted small">
                        Vereda Amacayacu, Puerto Asís, Putumayo.
                      </p>
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="dato-item d-flex align-items-start gap-3">
                    <div class="icon-box flex-shrink-0">
                      <font-awesome-icon :icon="['fas', 'phone']" />
                    </div>
                    <div>
                      <h6 class="mb-0">Teléfono</h6>
                      <p class="mb-0 text-muted small">+57 322 4225925</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="dato-item d-flex align-items-start gap-3">
                    <div class="icon-box flex-shrink-0">
                      <font-awesome-icon :icon="['fas', 'envelope']" />
                    </div>
                    <div class="overflow-hidden">
                      <h6 class="mb-0">Correo</h6>
                      <p class="mb-0 text-muted small correo-text">
                        kofancentroecoturistico@gmail.com
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Formulario -->
            <div class="form-wrapper p-4 flex-grow-1">
              <h2 class="mb-4">Envíanos un mensaje</h2>
              <form @submit.prevent="enviarFormulario">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Nombre Completo</label>
                    <input
                      v-model="nombre"
                      type="text"
                      class="form-control custom-input"
                      placeholder="Tu nombre"
                      required
                    />
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Correo Electrónico</label>
                    <input
                      v-model="email"
                      type="email"
                      class="form-control custom-input"
                      placeholder="correo@ejemplo.com"
                      required
                    />
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">Asunto</label>
                  <select v-model="asunto" class="form-select custom-input">
                    <option selected disabled>Selecciona una opción</option>
                    <option>Información de Reservas</option>
                    <option>Eventos y Grupos</option>
                    <option>Sugerencias</option>
                  </select>
                </div>
                <div class="mb-4">
                  <label class="form-label">Mensaje</label>
                  <textarea
                    v-model="mensaje"
                    class="form-control custom-input"
                    rows="4"
                    placeholder="Cuéntanos en qué podemos ayudarte..."
                  ></textarea>
                </div>
                <button type="submit" class="btn btn-kofan-submit w-100 py-3">
                  Enviar Mensaje
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Mapa compacto -->
    <section class="ubicacion-contacto">
      <div class="divisor-entrada">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none">
          <path
            d="M0,0V120H1200V0c-150,80-350,120-600,120S150,80,0,0Z"
            fill="var(--k-forest-soft)"
          ></path>
        </svg>
      </div>

      <div class="container">
        <div class="text-center mb-3">
          <h2 class="titulo-mapa">Nuestra ubicación en el Putumayo</h2>
        </div>

        <div class="mapa-wrapper">
          <iframe
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d15958.521652611322!2d-76.5355120619749!3d0.5560764129741063!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8e287e6540874957%3A0x9a11032de2a63510!2sCentro%20Ecoturistico%20Kofan!5e0!3m2!1ses!2sco!4v1762307375610!5m2!1ses!2sco"
            width="100%"
            height="360"
            style="border: 0"
            allowfullscreen
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
          ></iframe>
        </div>

        <div class="detalles-llegada">
          <div class="item-llegada">
            <font-awesome-icon icon="fa-solid fa-plane" class="icon-llegada" />
            <p>A solo 15 minutos del Aeropuerto 3 de Mayo.</p>
          </div>
          <div class="item-llegada">
            <font-awesome-icon icon="fa-solid fa-car" class="icon-llegada" />
            <p>Fácil acceso por vía principal con parqueadero privado.</p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from "vue";
import Swal from "sweetalert2";

const getBrandColor = (token, fallback) =>
  typeof window !== "undefined"
    ? getComputedStyle(document.documentElement).getPropertyValue(token).trim() || fallback
    : fallback;

const COLOR_FOREST = getBrandColor("--k-forest", "#0f3b2a");
const COLOR_CREAM = getBrandColor("--k-cream", "#fffcf8");

const nombre = ref("");
const email = ref("");
const asunto = ref("Selecciona una opción");
const mensaje = ref("");

const enviarFormulario = () => {
  Swal.fire({
    title: "¡Mensaje Enviado!",
    text: "Gracias por contactarnos. En breve un guía Kofán se comunicará contigo.",
    icon: "success",
    confirmButtonColor: COLOR_FOREST,
    confirmButtonText: "Entendido",
    background: COLOR_CREAM,
    backdrop: "rgba(15,59,42,0.4)",
  });
  nombre.value = "";
  email.value = "";
  mensaje.value = "";
  asunto.value = "Selecciona una opción";
};
</script>

<style scoped>
.card-redes h2 {
  color: white;
}

.titulo-contacto{
  color: white;
}

/* --- HERO --- */
.contacto-hero {
  background:
    linear-gradient(rgba(15, 59, 42, 0.7), rgba(15, 59, 42, 0.7)),
    url("@/img/entradaKofan.jpg") center/cover;
  height: 40vh;
}

.titulo-contacto {
  font-family: "Handlee", cursive;
  font-size: 3.5rem;
}

/* --- COLUMNA REDES --- */
.card-redes {
  background: var(--k-forest-soft);
  border-radius: 24px;
  color: var(--k-cream);
}

.red-link {
  text-decoration: none;
  transition: opacity 0.2s;
}
.red-link:hover {
  opacity: 0.85;
}

.red-icon-box {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  color: white;
  flex-shrink: 0;
  transition: transform 0.2s;
}
.red-link:hover .red-icon-box {
  transform: translateY(-3px);
}

.instagram {
  background: linear-gradient(
    45deg,
    #f09433,
    #e6683c,
    #dc2743,
    #cc2366,
    #bc1888
  );
}
.tiktok {
  background: #010101;
}
.whatsapp {
  background: #25d366;
}
.facebook {
  background: #1877f2;
}

/* --- INFO CONTACTO --- */
.card-info-contacto {
  background: var(--k-cream);
  border-radius: 20px;
  border: 1px solid var(--k-border);
}

.icon-box {
  width: 44px;
  height: 44px;
  background: var(--k-apple-soft);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  color: var(--k-forest);
}

/* --- FORMULARIO --- */
.form-wrapper {
  background: var(--k-offwhite);
  border-radius: 20px;
  border: 1px solid var(--k-border);
}

.custom-input {
  border: 1px solid var(--k-border);
  padding: 12px;
  border-radius: 10px;
  transition: all 0.3s;
  resize: none;
}

.custom-input:focus {
  border-color: var(--k-apple);
  box-shadow: 0 0 0 0.25rem rgba(139, 207, 91, 0.14);
}

.btn-kofan-submit {
  background: var(--k-forest);
  font-family: "Forum";
  color: var(--k-cream);
  border-radius: 10px;
  font-weight: 600;
  border: none;
  transition: background 0.3s;
}
.btn-kofan-submit:hover {
  background: var(--k-apple);
  color: var(--k-forest);
}

/* --- MAPA compacto --- */
.ubicacion-contacto {
  position: relative;
  background-color: var(--k-forest-soft);
  padding: 50px 20px 60px;
  color: var(--k-cream);
  margin-top: -1px;
}

.divisor-entrada {
  position: absolute;
  top: -1px;
  left: 0;
  width: 100%;
  line-height: 0;
  z-index: 10;
}

.divisor-entrada svg {
  display: block;
  width: 100%;
  height: 60px;
}

.titulo-mapa {
  font-family: "Handlee";
  font-size: 2rem;
  color: white;
  margin-bottom: 8px;
}

.mapa-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  border-radius: 16px;
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.2);
}

.detalles-llegada {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.item-llegada {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.05);
  padding: 10px 20px;
  border-radius: 16px;
}

.icon-llegada {
  font-size: 1.3rem;
  color: #82a994;
}
.item-llegada p {
  margin: 0;
  font-size: 0.9rem;
}

/* Evita que el correo largo desborde el contenedor */
.correo-text {
  word-break: break-all;
  overflow-wrap: break-word;
  font-size: 0.78rem;
}

/* --- RESPONSIVE --- */
@media (max-width: 768px) {
  .titulo-contacto {
    font-size: 2.5rem;
  }
  .ubicacion-contacto {
    padding: 50px 15px 40px;
  }
  .item-llegada {
    width: 100%;
    justify-content: center;
  }
}
</style>
