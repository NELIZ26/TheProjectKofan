<script setup>
import { ref, computed, watch } from "vue";
import Swal from "sweetalert2";
import PasswordInput from "@/components/form/PasswordInput.vue"; 

const props = defineProps({
  mostrarRol: { type: Boolean, default: false },
  cargando: { type: Boolean, default: false },
  usuarioEditando: { type: Object, default: null } 
});

const emit = defineEmits(["enviar"]);

const form = ref({
  tipo_persona: "", full_name: "", type_document: "", number_document: "",
  email: "", phone: "", country: "", city: "", password: "", role: "client"
});

const confirmPassword = ref("");

// Detectamos si estamos en modo edición
const isEditing = computed(() => !!props.usuarioEditando);



const resetForm = () => {
  form.value = {
    tipo_persona: "", full_name: "", type_document: "", number_document: "",
    email: "", phone: "", country: "", city: "", password: "", role: "client"
  };
  confirmPassword.value = "";
};

// 1. Mensaje visual para el Input (Solo muestra error si ya escribió algo y no coincide)
const passwordError = computed(() => {
  if (confirmPassword.value && form.value.password !== confirmPassword.value) {
    return "Las contraseñas no coinciden";
  }
  return "";
});

// 2. Validación inteligente para bloquear/desbloquear el Botón
const isFormInvalid = computed(() => {
  const basicFields = !form.value.full_name || !form.value.country || !form.value.city;
  const identityFields = !form.value.tipo_persona || !form.value.type_document || !form.value.number_document || !form.value.email;
  
  if (isEditing.value) {
    // 🟢 MODO EDICIÓN: Solo validamos los datos básicos, ignoramos las contraseñas
    return basicFields || identityFields;
  } else {
    // 🟢 MODO REGISTRO: Obligamos a que la clave tenga 8 caracteres y que ambas coincidan exactamente
    const invalidPassword = !form.value.password || form.value.password.length < 8 || form.value.password !== confirmPassword.value;
    return basicFields || identityFields || invalidPassword;
  }
});

const procesarFormulario = () => {
  if (!isEditing.value) {
    if (form.value.password.length < 8) {
      return Swal.fire({ icon: "warning", title: "Seguridad", text: "La clave debe tener 8+ caracteres.", confirmButtonColor: "#0f3b2a" });
    }
  }

  const datosAEnviar = { ...form.value };
  // Si editamos, el backend solo necesita los campos modificables, pero enviamos el ID
  if (isEditing.value) datosAEnviar.id = props.usuarioEditando.id;
  
  emit("enviar", datosAEnviar);
};
watch(() => props.usuarioEditando, (newVal) => {
  if (newVal) {
    form.value = { ...newVal, password: "" }; 
    confirmPassword.value = "";
  } else {
    resetForm();
  }
}, { immediate: true });


</script>

<template>
  <form @submit.prevent="procesarFormulario" class="row g-3">
    
    <div class="col-md-6">
      <label class="form-label fw-semibold small mb-1 text-muted">Tipo Persona</label>
      <select v-model="form.tipo_persona" class="form-select custom-input bg-light">
        <option value="Natural">Natural</option>
        <option value="Juridica">Jurídica</option>
      </select>
    </div>

    <div class="col-md-6">
      <label class="form-label fw-semibold small mb-1 text-muted">Nombre Completo</label>
      <input v-model="form.full_name" type="text" class="form-control custom-input" placeholder="Ej: Fabian">
    </div>

    <div class="col-md-6">
      <label class="form-label fw-semibold small mb-1" :class="{'text-muted': isEditing}">
        Documento <span v-if="!isEditing" class="text-danger">*</span>
      </label>
      
      <div v-if="!isEditing" class="input-group">
        <select v-model="form.type_document" class="form-select custom-input" style="max-width: 130px;" required>
          <option value="" disabled>Tipo...</option>
          <option value="CC">CC</option>
          <option value="CE">CE</option>
          <option value="PASAPORTE">Pasaporte</option>
          <option value="NIT">NIT</option>
        </select>
        <input v-model="form.number_document" type="text" class="form-control custom-input" placeholder="Ej: 12345678" required>
      </div>

      <div v-else class="input-group">
        <span class="input-group-text bg-light small fw-bold text-secondary border-end-0">
          {{ form.type_document || '---' }}
        </span>
        <input v-model="form.number_document" type="text" class="form-control custom-input bg-light" disabled>
      </div>
    </div>

    <div class="col-md-6">
      <label class="form-label fw-semibold small mb-1 text-muted">Correo Electrónico</label>
      <input v-model="form.email" type="email" class="form-control custom-input bg-light" :disabled="isEditing">
    </div>

    <div class="col-md-6">
      <label class="form-label fw-semibold small mb-1">Teléfono</label>
      <input v-model="form.phone" type="tel" class="form-control custom-input" placeholder="+57 3xx...">
    </div>

    <div class="col-md-3">
      <label class="form-label fw-semibold small mb-1">País</label>
      <input v-model="form.country" type="text" class="form-control custom-input">
    </div>

    <div class="col-md-3">
      <label class="form-label fw-semibold small mb-1">Ciudad</label>
      <input v-model="form.city" type="text" class="form-control custom-input">
    </div>

    <template v-if="!isEditing">
      <div class="col-md-6">
        <label class="form-label fw-semibold small mb-1">Contraseña <span class="text-danger">*</span></label>
        <PasswordInput v-model="form.password" placeholder="Mínimo 8 caracteres" />
      </div>
      <div class="col-md-6">
        <label class="form-label fw-semibold small mb-1">Confirmar Contraseña <span class="text-danger">*</span></label>
        <PasswordInput v-model="confirmPassword" placeholder="Repite la clave" :error="passwordError" />
      </div>
    </template>

    <div v-if="mostrarRol && !isEditing" class="col-12 mt-2">
      <label class="form-label fw-semibold small mb-1 text-primary">Rol en el Sistema</label>
      <select v-model="form.role" class="form-select custom-input border-primary">
        <option value="client">Cliente / Huésped</option>
        <option value="admin">Administrador</option>
      </select>
    </div>

    <div class="col-12 mt-4 d-flex justify-content-center">
      <button type="submit" class="btn btn-kofan px-5 py-2 shadow-sm w-100" :disabled="props.cargando || isFormInvalid">
        <span v-if="props.cargando" class="spinner-border spinner-border-sm me-2"></span>
        {{ props.cargando ? 'Procesando...' : (isEditing ? 'Guardar Cambios' : 'Registrar Usuario') }}
      </button>
    </div>

  </form>
</template>

<style scoped>
.custom-input:disabled {
  background-color: #f8f9fa !important;
  cursor: not-allowed;
  border-color: #e9ecef;
  color: #6c757d;
}
.btn-kofan {
  background-color: #0f3b2a;
  color: white;
  border-radius: 10px;
}
</style>