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
      Swal.fire({ icon: "warning", title: "Correo ya registrado", text: detail, confirmButtonColor: "#0f3b2a" });
    } else if (detail.toLowerCase().includes("documento")) {
      Swal.fire({ icon: "warning", title: "Documento ya registrado", text: detail, confirmButtonColor: "#0f3b2a" });
    } else {
      Swal.fire({
        icon: "error",
        title: "Error al registrarse",
        text: detail || "No pudimos crear tu cuenta. Por favor intenta de nuevo.",
        confirmButtonColor: "#0f3b2a",
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
      
      <div class="register-card shadow-lg row g-0">

        <div class="col-lg-4 d-none d-lg-flex flex-column justify-content-between p-4 p-xl-5 sidebar-kofan text-white">
          <div>
            <h2 class="handlee-font">Únete a la familia</h2>
            <p class="small mb-0">Regístrate para vivir experiencias únicas en el corazón del Putumayo.</p>
          </div>
          
          <div class="text-center mt-auto pb-3">
            <img src="@/img/Kofan.png" alt="Logo Kofán" class="img-fluid opacity-75 kofan-logo-sidebar">
          </div>
        </div>

        <div class="col-lg-8 p-4 p-md-5 bg-white">
          
          <div class="text-center mb-4">
            <h2 class="fw-bold verde-kofan mb-1">Crear Cuenta</h2>
            <div class="divider mx-auto"></div>
          </div>

          <FormularioRegistro 
            :mostrarRol="false" 
            :cargando="isLoading"
            @enviar="registrarCliente" 
          />

          <div class="col-12 text-center mt-3">
            <p class="text-muted small mb-0">
              ¿Ya tienes una cuenta?
              <router-link :to="{ name: 'login' }" class="verde-kofan fw-bold text-decoration-none">Inicia Sesión</router-link>
            </p>
          </div>

        </div>

      </div>
    </div>
  </main>
</template>

<style scoped>
/* Fondo general */
.auth-page {
  background-color: #f8f9fa;
  min-height: 100vh;
}

/* Tarjeta principal - Bordes MUY redondos (25px) */
.register-card {
  border-radius: 25px; /* Aumentado significativamente */
  overflow: hidden; /* Importante para que las columnas respeten el redondeo */
  max-width: 950px;
  width: 100%;
}

/* Sidebar verde */
.sidebar-kofan {
  background-color: #0f3b2a !important;
}

/* Logo */
.kofan-logo-sidebar {
  max-height: 220px;
  object-fit: contain;
}

/* Botón - Bordes redondos (15px) */
.btn-kofan {
  background-color: #0f3b2a !important;
  border-color: #0f3b2a !important;
  color: white !important;
  border-radius: 15px; /* Aumentado */
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.btn-kofan:hover {
  background-color: #0a291d !important;
  border-color: #0a291d !important;
}

.btn-kofan:disabled {
  background-color: rgba(15, 59, 42, 0.65) !important;
  border-color: rgba(15, 59, 42, 0.65) !important;
  opacity: 1;
}

/* Inputs y Selects - Bordes MUY redondos (18px) */
.custom-input {
  border-radius: 18px; /* Aumentado significativamente */
  padding: 0.6rem 0.75rem;
  font-size: 0.9rem;
  border-color: #dee2e6;
}

/* Label de input */
.form-label {
  font-size: 0.85rem;
}

/* Elementos visuales */
.divider {
  width: 50px;
  height: 2px;
  background-color: #0f3b2a;
}

.handlee-font {
  font-family: 'Handlee', cursive;
}

.verde-kofan {
  color: #0f3b2a !important;
}

/* Estilos de error para PasswordInput */
:deep(.is-invalid input) {
  border-color: #dc3545 !important;
}
:deep(.invalid-feedback) {
  font-size: 0.8rem;
}

/* Para aplicar el mismo redondeo al componente PasswordInput */
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