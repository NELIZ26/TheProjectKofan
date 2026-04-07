<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import apiClient from "@/api/apiClient";
import Swal from "sweetalert2";

const auth = useAuthStore();

// Estado del Formulario
const formData = ref({
  full_name: auth.user?.full_name || "",
  phone: auth.user?.phone || "",
  country: auth.user?.country || "Colombia",
  city: auth.user?.city || "",
  email: auth.user?.email || "",
  number_document: auth.user?.number_document || ""
});

const saveProfile = async () => {
  const result = await Swal.fire({
    title: '¿Confirmar cambios?',
    text: "Se actualizará tu información personal",
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#0f3b2a',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Sí, guardar',
    cancelButtonText: 'Cancelar'
  });

  if (result.isConfirmed) {
    try {
      const payload = {
        full_name: formData.value.full_name,
        phone: formData.value.phone,
        country: formData.value.country,
        city: formData.value.city
      };

      const { data } = await apiClient.patch("/users/update-me", payload);

      if (auth.updateUser) auth.updateUser(data.user);

      Swal.fire({ title: '¡Actualizado!', text: 'Tus datos se han guardado.', icon: 'success', confirmButtonColor: '#198754' });
      
    } catch (error) {
      const errorMsg = error.response?.data?.detail || "Hubo un problema al actualizar los datos.";
      Swal.fire("Error", errorMsg, "error");
    }
  }
};
</script>

<template>
  <div class="settings-container p-1">
    
    <div class="mb-4">
      <h3 class="fw-bold text-dark mb-1">Configuración</h3>
      <p class="text-muted small mb-0">Actualiza tu información de contacto personal.</p>
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="card-header bg-white p-4 border-bottom d-flex align-items-center">
        <h5 class="fw-bold mb-0 verde-kofan"><i class="bi bi-person-gear me-2"></i> Mis Datos</h5>
      </div>
      
      <div class="card-body p-4 p-md-5">
        <form @submit.prevent="saveProfile">
          <div class="row g-4 mb-4">
            <div class="col-md-6">
              <label class="form-label fw-bold text-secondary small">Nombre Completo</label>
              <div class="input-group shadow-sm rounded">
                <span class="input-group-text bg-white text-muted border-end-0"><i class="bi bi-person"></i></span>
                <input type="text" class="form-control border-start-0 ps-0" v-model="formData.full_name" required />
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-bold text-secondary small">Teléfono</label>
              <div class="input-group shadow-sm rounded">
                <span class="input-group-text bg-white text-muted border-end-0"><i class="bi bi-telephone"></i></span>
                <input type="text" class="form-control border-start-0 ps-0" v-model="formData.phone" required />
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-bold text-secondary small">País</label>
              <div class="input-group shadow-sm rounded">
                <span class="input-group-text bg-white text-muted border-end-0"><i class="bi bi-globe-americas"></i></span>
                <input type="text" class="form-control border-start-0 ps-0" v-model="formData.country" />
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-bold text-secondary small">Ciudad de Residencia</label>
              <div class="input-group shadow-sm rounded">
                <span class="input-group-text bg-white text-muted border-end-0"><i class="bi bi-building"></i></span>
                <input type="text" class="form-control border-start-0 ps-0" v-model="formData.city" />
              </div>
            </div>
          </div>

          <div class="alert alert-success bg-opacity-10 border border-success-subtle d-flex align-items-center small text-dark rounded-4 p-3">
            <i class="bi bi-shield-lock-fill fs-4 me-3 text-success"></i>
            <div>
              <strong>Seguridad Kofán:</strong> Tu correo electrónico ({{ formData.email }}) y número de documento ({{ formData.number_document }}) están protegidos y no pueden ser alterados.
            </div>
          </div>

          <div class="mt-4 d-flex justify-content-end">
            <button type="submit" class="btn btn-dark px-5 py-2 shadow-sm rounded-pill fw-medium" style="background-color: #0f3b2a; border: none;">
              <i class="bi bi-save me-2"></i> Guardar Cambios
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.verde-kofan { color: #0f3b2a; }
.input-group-text { border-color: #dee2e6; }
.form-control { border-color: #dee2e6; }
.form-control:focus { border-color: #0f3b2a; box-shadow: 0 0 0 0.25rem rgba(15, 59, 42, 0.1); }
.form-control:focus + .input-group-text { border-color: #0f3b2a; }
</style>