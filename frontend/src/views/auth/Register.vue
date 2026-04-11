<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import Swal from "sweetalert2";
import { register, login } from "@/services/authServices";

// 1. 🟢 IMPORTAMOS TU NUEVO COMPONENTE "LEGO"
import FormularioRegistro from "@/components/FormularioRegistro.vue";

const auth = useAuthStore();
const router = useRouter();
const isLoading = ref(false);

const getBrandColor = (token, fallback) =>
  typeof window !== "undefined"
    ? getComputedStyle(document.documentElement).getPropertyValue(token).trim() || fallback
    : fallback;

const COLOR_FOREST = getBrandColor("--k-forest", "#0f3b2a");

// 2. 🟢 ESTA FUNCIÓN ATRAPA LOS DATOS CUANDO EL FORMULARIO HACE EL "EMIT"
const registrarCliente = async (datosDelFormulario) => {
  isLoading.value = true;

  try {
    // 1. Registrar
    await register({
      tipo_persona:    datosDelFormulario.tipo_persona,
      full_name:       datosDelFormulario.full_name,
      type_document:   datosDelFormulario.type_document,
      number_document: datosDelFormulario.number_document,
      email:           datosDelFormulario.email,
      phone:           datosDelFormulario.phone || null,
      country:         datosDelFormulario.country,
      city:            datosDelFormulario.city,
      password:        datosDelFormulario.password,
    });

    // 2. Login automático
    const tokenData = await login({ username: datosDelFormulario.email, password: datosDelFormulario.password });

    // 3. Guardar sesión
    auth.login(
      { email: datosDelFormulario.email, full_name: datosDelFormulario.full_name, role: "client" },
      tokenData.access_token,
      tokenData.token_type
    );

    // 4. Notificación
    await Swal.fire({
      icon: "success",
      title: "¡Bienvenido a Kofán!",
      text: `Hola ${datosDelFormulario.full_name}, tu cuenta ha sido creada con éxito.`,
      timer: 2500,
      showConfirmButton: false,
    });

    // 5. Redirigir
    router.push({ name: "account-profile" });

  } catch (error) {
    const detail = error.response?.data?.detail || "";

    if (detail.toLowerCase().includes("correo")) {
      Swal.fire({ icon: "warning", title: "Correo ya registrado", text: detail, confirmButtonColor: COLOR_FOREST });
    } else if (detail.toLowerCase().includes("documento")) {
      Swal.fire({ icon: "warning", title: "Documento ya registrado", text: detail, confirmButtonColor: COLOR_FOREST });
    } else {
      Swal.fire({
        icon: "error",
        title: "Error al registrarse",
        text: detail || "No pudimos crear tu cuenta. Por favor intenta de nuevo.",
        confirmButtonColor: COLOR_FOREST,
      });
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <main class="auth-page py-5 mt-3">
    <div class="container d-flex justify-content-center">
      <div class="register-card row g-0">

        <div class="col-lg-4 d-none d-lg-flex flex-column justify-content-between p-4 p-xl-5 sidebar-kofan">
          <div>
            <p class="sidebar-kicker mb-2">Comunidad Kofán</p>
            <h2 class="sidebar-title">Únete a nuestra comunidad y gestiona con armonía</h2>
            <p class="sidebar-copy mb-0">Crea tu cuenta para organizar cada experiencia con calma y claridad.</p>
          </div>
          
          <div class="text-center mt-auto pb-3">
            <img src="@/img/Kofan.png" alt="Logo Kofán" class="img-fluid opacity-75 kofan-logo-sidebar">
          </div>
        </div>

        <div class="col-lg-8 p-4 p-md-5 form-panel">
          <div class="text-center mb-4">
            <h2 class="register-title mb-2">Crear Cuenta</h2>
            <p class="register-copy mb-0">Tu acceso al ecosistema Kofán comienza aquí.</p>
          </div>

          <FormularioRegistro 
            :mostrarRol="false" 
            :cargando="isLoading"
            @enviar="registrarCliente" 
          />

          <div class="col-12 text-center mt-3">
            <p class="helper-copy mb-0">
              ¿Ya tienes una cuenta?
              <router-link :to="{ name: 'login' }" class="auth-link text-decoration-none">Inicia Sesión</router-link>
            </p>
          </div>

        </div>

      </div>
    </div>
  </main>
</template>

<style scoped>
.auth-page {
  background-color: var(--k-cream);
  min-height: 100vh;
  color: var(--k-forest);
}

.register-card {
  border-radius: 22px;
  overflow: hidden;
  max-width: 950px;
  width: 100%;
  background: var(--k-cream) !important;
  border: 1px solid var(--k-border);
  box-shadow: 0 12px 30px rgba(15, 59, 42, 0.08);
}

.sidebar-kofan {
  background-color: var(--k-sky-soft);
  color: var(--k-forest);
  border-right: 1px solid rgba(52, 152, 219, 0.16);
}

.sidebar-title,
.register-title,
:deep(.form-label) {
  font-family: "Forum", serif;
  color: var(--k-forest) !important;
}

.sidebar-kicker,
.sidebar-copy,
.register-copy,
.helper-copy,
.auth-link,
:deep(.custom-input),
:deep(.custom-input::placeholder),
:deep(.form-control::placeholder),
:deep(.form-select),
:deep(.invalid-feedback),
:deep(.btn-kofan),
:deep(.input-group-text) {
  font-family: "Handlee", cursive;
}

.kofan-logo-sidebar {
  max-height: 220px;
  object-fit: contain;
}

.form-panel {
  background: var(--k-cream);
}

.sidebar-title {
  font-size: 2rem;
  line-height: 1.15;
}

.register-title {
  font-size: 2.1rem;
}

.sidebar-copy,
.register-copy,
.helper-copy {
  color: var(--k-muted);
}

.auth-link {
  color: var(--k-forest);
}

:deep(.custom-input),
:deep(.form-control),
:deep(.form-select),
:deep(.input-group-text) {
  background-color: var(--k-cream) !important;
  border-color: var(--k-border) !important;
  color: var(--k-forest) !important;
  border-radius: 18px !important;
}

:deep(.form-control:focus),
:deep(.form-select:focus) {
  border-color: var(--k-apple) !important;
  box-shadow: 0 0 0 0.18rem rgba(139, 207, 91, 0.18) !important;
}

:deep(.custom-input::placeholder),
:deep(.form-control::placeholder) {
  color: rgba(15, 59, 42, 0.58) !important;
  opacity: 1;
}

:deep(.btn-kofan) {
  background-color: var(--k-forest) !important;
  border-color: var(--k-forest) !important;
  color: var(--k-cream) !important;
  border-radius: 999px !important;
  box-shadow: none !important;
  font-weight: 700;
}

:deep(.btn-kofan:hover) {
  background-color: var(--k-apple) !important;
  border-color: var(--k-apple) !important;
  color: var(--k-forest) !important;
}

:deep(.btn-kofan:disabled) {
  background-color: rgba(139, 207, 91, 0.65) !important;
  border-color: rgba(139, 207, 91, 0.65) !important;
  opacity: 1;
}

:deep(.invalid-feedback) {
  font-size: 0.85rem;
}

:deep(.custom-input-p .input-group) {
  border-radius: 18px !important;
  overflow: hidden !important;
}

:deep(.custom-input-p .form-control) {
  border-radius: 18px 0 0 18px !important;
}

:deep(.custom-input-p .input-group-text) {
  border-radius: 0 18px 18px 0 !important;
}
</style>