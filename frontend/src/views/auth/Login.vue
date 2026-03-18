<template>
  <section
    class="auth-section d-flex align-items-center justify-content-center"
  >
    <div class="auth-container row g-0 shadow-lg">
      <div class="col-md-6 d-none d-md-block auth-image">
        <div
          class="auth-overlay d-flex flex-column justify-content-center p-5 text-white"
        >
          <h2 class="titulo-auth">Bienvenido de vuelta</h2>
          <p>
            Accede para gestionar tus reservas y vivir la experiencia Kofán.
          </p>
        </div>
      </div>

      <div
        class="col-md-6 p-5 bg-white d-flex flex-column justify-content-center"
      >
        <div class="text-center mb-4">
          <img src="@/img/Kofan.png" width="100" alt="Logo" />
          <h3 class="mt-3 fw-bold">Iniciar Sesión</h3>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label">Correo Electrónico</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"
                ><i class="fa fa-envelope"></i
              ></span>
              <input
                v-model="email"
                type="email"
                class="form-control border-start-0 bg-light"
                placeholder="ejemplo@correo.com"
                required
              />
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label">Contraseña</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-end-0"
                ><i class="fa fa-lock"></i
              ></span>
              <input
                v-model="password"
                type="password"
                class="form-control border-start-0 bg-light"
                placeholder="********"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            class="btn btn-kofan w-100 py-2 mb-3"
            :disabled="isLoading"
          >
            <span
              v-if="isLoading"
              class="spinner-border spinner-border-sm me-2"
            ></span>
            {{ isLoading ? "Cargando..." : "Ingresar" }}
          </button>
        </form>

        <p class="text-center mt-3">
          ¿No tienes cuenta?
          <router-link to="/register" class="text-success fw-bold"
            >Regístrate aquí</router-link
          >
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.auth-section {
  min-height: 100vh;
  background: #fffdfc;
  padding: 10px;
}

.auth-container {
  width: 100%;
  max-width: 900px;
  border-radius: 20px;
  overflow: hidden;
  background: white;
}

.auth-image {
  background: url("@/img/entradaKofan.jpg") center/cover;
  position: relative;
  min-height: 500px;
}

.auth-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 59, 42, 0.6);
  backdrop-filter: blur(2px);
}

.titulo-auth {
  font-family: "Handlee", cursive;
  font-size: 2.5rem;
}

.btn-kofan {
  background: #0f3b2a;
  color: white;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-kofan:hover {
  background: #1a5c43;
  transform: translateY(-2px);
}

.input-group-text {
  color: #0f3b2a;
}
</style>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { login, getUserProfile } from "@/services/authServices"; // Verifica que el archivo sea authServices.js
import Swal from "sweetalert2";

const auth = useAuthStore();
const router = useRouter();

const email = ref("");
const password = ref("");
const isLoading = ref(false);

const handleLogin = async () => {
  if (!email.value || !password.value) {
    Swal.fire("Atención", "Por favor completa todos los campos", "warning");
    return;
  }

  isLoading.value = true;

  try {
    // 1. Autenticación contra el Backend
    // Enviamos el email como 'username' ya que OAuth2 suele usar ese campo
    const loginResponse = await login({
      username: email.value.trim(),
      password: password.value,
    });

    // 2. Guardar el token en localStorage PRIMERO (lo necesita el interceptor)
    localStorage.setItem('token', loginResponse.access_token);
    localStorage.setItem('token_type', loginResponse.token_type);

    // 3. Obtener el perfil completo (ahora el interceptor tiene el token)
    const userData = await getUserProfile();

    // 4. Actualizar el estado en Pinia
    auth.login(userData, loginResponse.access_token, loginResponse.token_type);

    // 5. Mensaje de éxito
    Swal.fire({
      icon: "success",
      title: `¡Bienvenido, ${userData.full_name}!`,
      text: "Acceso concedido al paraíso.",
      timer: 2000,
      showConfirmButton: false,
    });

    // 6. Redirección inteligente basada en tu index.js
    // Revisa si tu API devuelve 'rol' o 'role'
    const userRole = userData.rol || userData.role;

    if (userRole === "admin") {
      router.push({ name: "admin-dashboard" });
    } else {
      router.push({ name: "account-profile" });
    }
  } catch (error) {
    console.error("Error en login:", error);
    const msg =
      error.response?.data?.detail || "Correo o contraseña incorrectos";
    Swal.fire("Error de Acceso", msg, "error");
  } finally {
    isLoading.value = false;
  }
};
</script>
