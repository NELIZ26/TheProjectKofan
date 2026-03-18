<template>
  <main class="auth-page py-5">
    <div class="container d-flex justify-content-center">
      <div class="register-card shadow-lg row g-0">

        <div class="col-lg-4 d-none d-lg-block register-sidebar text-white p-4">
          <div class="h-100 d-flex flex-column justify-content-between">
            <div>
              <h2 class="handlee-font">Únete a la familia</h2>
              <p class="small">Regístrate para vivir experiencias únicas en el corazón del Putumayo.</p>
            </div>
            <img src="@/img/Kofan.png" alt="Logo Kofán" class="img-fluid opacity-50">
          </div>
        </div>

        <div class="col-lg-8 p-4 p-md-5 bg-white">
          <div class="text-center mb-4">
            <h2 class="fw-bold verde-kofan">Crear Cuenta</h2>
            <div class="divider mx-auto"></div>
          </div>

          <form @submit.prevent="submit" class="row g-3">

            <div class="col-md-6">
              <label class="form-label fw-semibold">Tipo Persona <span class="text-danger">*</span></label>
              <select v-model="form.tipo_persona" class="form-select custom-input">
                <option value="">Seleccione...</option>
                <option value="natural">Natural</option>
                <option value="juridica">Jurídica</option>
              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">Nombre Completo <span class="text-danger">*</span></label>
              <input v-model="form.full_name" type="text" class="form-control custom-input" placeholder="Ej: Juan Pérez">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">Tipo Documento <span class="text-danger">*</span></label>
              <select v-model="form.type_document" class="form-select custom-input">
                <option value="">Seleccione...</option>
                <option value="CC">Cédula de Ciudadanía</option>
                <option value="CE">Cédula Extranjera</option>
                <option value="PASAPORTE">Pasaporte</option>
                <option value="NIT">NIT</option>
              </select>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">Número Documento <span class="text-danger">*</span></label>
              <input v-model="form.number_document" type="text" class="form-control custom-input" placeholder="12345678">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">Correo Electrónico <span class="text-danger">*</span></label>
              <input v-model="form.email" type="email" class="form-control custom-input" placeholder="correo@ejemplo.com">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">Teléfono</label>
              <input v-model="form.phone" type="tel" class="form-control custom-input" placeholder="+57 3xx xxx xxxx">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">País <span class="text-danger">*</span></label>
              <input v-model="form.country" type="text" class="form-control custom-input" placeholder="Ej: Colombia">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold">Ciudad <span class="text-danger">*</span></label>
              <input v-model="form.city" type="text" class="form-control custom-input" placeholder="Ej: Sibundoy">
            </div>

            <div class="col-12">
              <label class="form-label fw-semibold">Contraseña <span class="text-danger">*</span></label>
              <input v-model="form.password" type="password" class="form-control custom-input" placeholder="Min. 8 caracteres">
            </div>

            <div class="col-12 mt-4">
              <button type="submit" class="btn btn-kofan w-100 py-3 shadow-sm" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ isLoading ? 'Creando cuenta...' : 'Completar Registro' }}
              </button>
            </div>

            <div class="col-12 text-center mt-3">
              <p class="text-muted small">
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

<script setup>
import { ref, reactive } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import Swal from "sweetalert2";
import { register, login } from "@/services/authServices";

const auth = useAuthStore();
const router = useRouter();
const isLoading = ref(false);

const form = reactive({
  tipo_persona: "",
  full_name: "",
  type_document: "",
  number_document: "",
  email: "",
  phone: "",
  country: "",
  city: "",
  password: "",
});

const submit = async () => {
  // Validación campos obligatorios (phone es opcional)
  if (
    !form.tipo_persona || !form.full_name  || !form.type_document ||
    !form.number_document || !form.email  || !form.country ||
    !form.city || !form.password
  ) {
    return Swal.fire({
      icon: "warning",
      title: "Campos incompletos",
      text: "Por favor completa todos los campos obligatorios.",
      confirmButtonColor: "#0f3b2a",
    });
  }

  if (form.password.length < 8) {
    return Swal.fire({
      icon: "warning",
      title: "Contraseña muy corta",
      text: "La contraseña debe tener al menos 8 caracteres.",
      confirmButtonColor: "#0f3b2a",
    });
  }

  isLoading.value = true;

  try {
    // 1. Registrar → POST /register/
    await register({
      tipo_persona:    form.tipo_persona,
      full_name:       form.full_name,
      type_document:   form.type_document,
      number_document: form.number_document,
      email:           form.email,
      phone:           form.phone || null,
      country:         form.country,
      city:            form.city,
      password:        form.password,
    });

    // 2. Login automático → POST /auth/login
    // El backend no devuelve token en el registro, por eso hacemos login inmediatamente
    const tokenData = await login({ username: form.email, password: form.password });

    // 3. Guardar sesión en el store
    auth.login(
      { email: form.email, full_name: form.full_name, role: "client" },
      tokenData.access_token,
      tokenData.token_type
    );

    // 4. Notificación de éxito
    await Swal.fire({
      icon: "success",
      title: "¡Bienvenido a Kofán!",
      text: `Hola ${form.full_name}, tu cuenta ha sido creada con éxito.`,
      timer: 2500,
      showConfirmButton: false,
    });

    // 5. Redirigir al perfil
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

<style scoped>
.auth-page {
  background-color: #f8f9fa;
  min-height: 100vh;
  padding-top: 100px;
  margin-top: 50px;
}

.register-card {
  max-width: 900px;
  width: 100%;
  border-radius: 25px;
  overflow: hidden;
  border: none;
}

.register-sidebar {
  background: linear-gradient(rgba(15, 59, 42, 0.85), rgba(15, 59, 42, 0.85)),
              url('@/img/fondo3.png') center/cover;
}

.verde-kofan { color: #0f3b2a; }

.handlee-font { font-family: 'Handlee', cursive; }

.divider {
  width: 50px;
  height: 4px;
  background-color: #2ecc71;
  border-radius: 2px;
}

.custom-input {
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 10px 15px;
  background-color: #fdfdfd;
}

.custom-input:focus {
  border-color: #0f3b2a;
  box-shadow: 0 0 0 0.25rem rgba(15, 59, 42, 0.1);
}

.btn-kofan {
  background-color: #0f3b2a;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-kofan:hover:not(:disabled) {
  background-color: #1a5c43;
  transform: translateY(-2px);
}

.btn-kofan:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>