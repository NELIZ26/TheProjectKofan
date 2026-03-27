<script setup>
import { ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import Swal from "sweetalert2";
import { register, login } from "@/services/authServices";
import PasswordInput from "@/components/form/PasswordInput.vue"; // Asegúrate de que la ruta sea correcta

const auth = useAuthStore();
const router = useRouter();
const isLoading = ref(false);

const form = ref({
  tipo_persona: "",
  full_name: "", // Si tu backend pide names y surnames por separado, debes cambiar esto
  type_document: "",
  number_document: "",
  email: "",
  phone: "",
  country: "",
  city: "",
  password: "",
});

const confirmPassword = ref("");

// Lógica de validación
const passwordsMatch = computed(() => {
  if (!form.value.password || !confirmPassword.value) return true;
  return form.value.password === confirmPassword.value;
});

const isFormInvalid = computed(() => {
  return (
    !form.value.tipo_persona ||
    !form.value.full_name ||
    !form.value.type_document ||
    !form.value.number_document ||
    !form.value.email ||
    !form.value.country ||
    !form.value.city ||
    !form.value.password ||
    !passwordsMatch.value
  );
});

const submit = async () => {
  // Validación de seguridad adicional
  if (!passwordsMatch.value) {
    return Swal.fire({
      icon: "warning",
      title: "Contraseñas no coinciden",
      text: "Por favor, asegúrate de que ambas contraseñas sean iguales.",
      confirmButtonColor: "#0f3b2a",
    });
  }

  if (form.value.password.length < 8) {
    return Swal.fire({
      icon: "warning",
      title: "Contraseña muy corta",
      text: "La contraseña debe tener al menos 8 caracteres.",
      confirmButtonColor: "#0f3b2a",
    });
  }

  isLoading.value = true;

  try {
    // 1. Registrar
    await register({
      tipo_persona:    form.value.tipo_persona,
      full_name:       form.value.full_name,
      type_document:   form.value.type_document,
      number_document: form.value.number_document,
      email:           form.value.email,
      phone:           form.value.phone || null,
      country:         form.value.country,
      city:            form.value.city,
      password:        form.value.password,
    });

    // 2. Login automático
    const tokenData = await login({ username: form.value.email, password: form.value.password });

    // 3. Guardar sesión
    auth.login(
      { email: form.value.email, full_name: form.value.full_name, role: "client" },
      tokenData.access_token,
      tokenData.token_type
    );

    // 4. Notificación
    await Swal.fire({
      icon: "success",
      title: "¡Bienvenido a Kofán!",
      text: `Hola ${form.value.full_name}, tu cuenta ha sido creada con éxito.`,
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

          <form @submit.prevent="submit" class="row g-3">
            
            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">Tipo Persona <span class="text-danger">*</span></label>
              <select v-model="form.tipo_persona" class="form-select custom-input">
                <option value="">Seleccione...</option>
                <option value="natural">Natural</option>
                <option value="juridica">Jurídica</option>
              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">Nombre Completo <span class="text-danger">*</span></label>
              <input v-model="form.full_name" type="text" class="form-control custom-input" placeholder="Ej: Juan Pérez">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">Tipo Documento <span class="text-danger">*</span></label>
              <select v-model="form.type_document" class="form-select custom-input">
                <option value="">Seleccione...</option>
                <option value="CC">Cédula de Ciudadanía</option>
                <option value="CE">Cédula Extranjera</option>
                <option value="PASAPORTE">Pasaporte</option>
                <option value="NIT">NIT</option>
              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">Número Documento <span class="text-danger">*</span></label>
              <input v-model="form.number_document" type="text" class="form-control custom-input" placeholder="12345678">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">Correo Electrónico <span class="text-danger">*</span></label>
              <input v-model="form.email" type="email" class="form-control custom-input" placeholder="correo@ejemplo.com">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">Teléfono</label>
              <input v-model="form.phone" type="tel" class="form-control custom-input" placeholder="+57 3xx xxx xxxx">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">País <span class="text-danger">*</span></label>
              <input v-model="form.country" type="text" class="form-control custom-input" placeholder="Ej: Colombia">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">Ciudad <span class="text-danger">*</span></label>
              <input v-model="form.city" type="text" class="form-control custom-input" placeholder="Ej: Sibundoy">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">Contraseña <span class="text-danger">*</span></label>
              <PasswordInput v-model="form.password" placeholder="Min. 8 caracteres" class="custom-input-p" />
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold small mb-1">Confirmar Contraseña <span class="text-danger">*</span></label>
              <PasswordInput 
                v-model="confirmPassword" 
                placeholder="Repite la contraseña" 
                :error="!passwordsMatch ? 'Contraseñas no coinciden' : ''"
                class="custom-input-p"
              />
            </div>

            <div class="col-12 mt-4 d-flex justify-content-center">
              <button type="submit" class="btn btn-kofan px-5 py-2 shadow-sm" :disabled="isLoading || isFormInvalid">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ isLoading ? 'Creando cuenta...' : 'Completar Registro' }}
              </button>
            </div>

            <div class="col-12 text-center mt-3">
              <p class="text-muted small mb-0">
                ¿Ya tienes una cuenta?
                <router-link :to="{ name: 'login' }" class="verde-kofan fw-bold text-decoration-none">Inicia Sesión</router-link>
              </p>
            </div>

          </form>
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