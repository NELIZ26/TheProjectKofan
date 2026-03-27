<script setup>
import { ref, onMounted } from 'vue';
// IMPORTANTE: Tendremos que crear este servicio en el paso 2
import { fetchConfig, saveConfig, uploadLogo } from '@/services/configService';

const isLoading = ref(true);
const isSaving = ref(false);
const message = ref({ text: '', type: '' });
const fileInput = ref(null);

const base = import.meta.env.VITE_BACKEND_URL;

const config = ref({
  hotel_name: 'Kofán Hospedaje',
  logo_url: '',
  contact_email: '',
  phone: '',
  address: '',
  check_in_time: '15:00',
  check_out_time: '11:00',
  currency: 'COP',
  social_facebook: '',
  social_instagram: '',
  tax_percentage: 0
});

const handleLogoUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await uploadLogo(formData);
    config.value.logo_url = res.logo_url;
    message.value = { text: 'Logo subido correctamente', type: 'success' };
  } catch (error) {
    message.value = { text: 'Error al subir el logo', type: 'danger' };
  }
};

const loadSettings = async () => {
  try {
    const data = await fetchConfig();
    if (data) config.value = { ...config.value, ...data };
  } catch (error) {
    console.error("Error cargando configuración", error);
  } finally {
    isLoading.value = false;
  }
};

const handleSave = async () => {
  isSaving.value = true;
  message.value = { text: '', type: '' };
  
  try {
    await saveConfig(config.value);
    message.value = { text: 'Configuración actualizada con éxito', type: 'success' };
  } catch (error) {
    message.value = { text: 'Error al guardar los cambios', type: 'danger' };
  } finally {
    isSaving.value = false;
    setTimeout(() => message.value.text = '', 3000);
  }
};

onMounted(loadSettings);
</script>

<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold verde-kofan"><i class="bi bi-gear-fill me-2"></i>Configuración del Sistema</h2>
      <button 
        @click="handleSave" 
        class="btn btn-kofan px-4 shadow-sm" 
        :disabled="isSaving || isLoading"
      >
        <span v-if="isSaving" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-cloud-check me-2"></i>
        Guardar Cambios
      </button>
    </div>

    <div v-if="message.text" :class="['alert alert-dismissible fade show shadow-sm', `alert-${message.type}`]" style="border-radius: 12px;">
      {{ message.text }}
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border verde-kofan" role="status"></div>
      <p class="mt-2 text-muted">Cargando parámetros...</p>
    </div>

    <div v-else class="card config-card shadow-sm border-0">
      <div class="card-body p-0">
        <div class="row g-0">
          <div class="col-md-3 border-end bg-light p-3 sidebar-config">
            <div class="nav flex-column nav-pills" id="v-pills-tab" role="tablist">
              <button class="nav-link active text-start mb-2" data-bs-toggle="pill" data-bs-target="#general">
                <i class="bi bi-info-circle me-2"></i>General
              </button>
              <button class="nav-link text-start mb-2" data-bs-toggle="pill" data-bs-target="#hotel">
                <i class="bi bi-building me-2"></i>Operaciones
              </button>
              <button class="nav-link text-start mb-2" data-bs-toggle="pill" data-bs-target="#social">
                <i class="bi bi-share me-2"></i>Redes Sociales
              </button>
            </div>
          </div>

          <div class="col-md-9 p-4 p-lg-5">
            <form @submit.prevent="handleSave">
              <div class="tab-content">
                
                <div class="tab-pane fade show active" id="general">
                  <h5 class="mb-4 fw-bold text-dark">Información Principal</h5>
                  <div class="row g-3">
                    <div class="col-md-12 mb-4 text-center">
                      <label class="form-label d-block fw-semibold text-muted mb-3">Logo Actual</label>
                      <div class="mb-3">
                        <img 
                          :src="config.logo_url ? `${base}${config.logo_url}` : '@/img/Kofan.png'" 
                          alt="Logo Preview" 
                          class="img-thumbnail shadow-sm p-2"
                          style="max-height: 120px; border-radius: 15px;"
                        >
                      </div>
                      <input type="file" ref="fileInput" @change="handleLogoUpload" class="d-none" accept="image/*">
                      <button type="button" class="btn btn-outline-secondary btn-sm" style="border-radius: 10px;" @click="fileInput.click()">
                        <i class="bi bi-camera me-2"></i>Cambiar Logo
                      </button>
                    </div>
                    
                    <div class="col-md-12">
                      <label class="form-label fw-semibold small ms-1">Nombre del Hospedaje</label>
                      <input v-model="config.hotel_name" type="text" class="form-control custom-input">
                    </div>
                    <div class="col-md-6">
                      <label class="form-label fw-semibold small ms-1">Email de Contacto</label>
                      <input v-model="config.contact_email" type="email" class="form-control custom-input">
                    </div>
                    <div class="col-md-6">
                      <label class="form-label fw-semibold small ms-1">Teléfono Principal</label>
                      <input v-model="config.phone" type="text" class="form-control custom-input">
                    </div>
                    <div class="col-md-12">
                      <label class="form-label fw-semibold small ms-1">Dirección Física</label>
                      <input v-model="config.address" type="text" class="form-control custom-input">
                    </div>
                  </div>
                </div>

                <div class="tab-pane fade" id="hotel">
                  <h5 class="mb-4 fw-bold text-dark">Parámetros de Reserva</h5>
                  <div class="row g-3">
                    <div class="col-md-6">
                      <label class="form-label fw-semibold small ms-1">Hora de Check-in</label>
                      <input v-model="config.check_in_time" type="time" class="form-control custom-input">
                    </div>
                    <div class="col-md-6">
                      <label class="form-label fw-semibold small ms-1">Hora de Check-out</label>
                      <input v-model="config.check_out_time" type="time" class="form-control custom-input">
                    </div>
                    <div class="col-md-6">
                      <label class="form-label fw-semibold small ms-1">Moneda Base</label>
                      <select v-model="config.currency" class="form-select custom-input">
                        <option value="COP">Peso Colombiano (COP)</option>
                        <option value="USD">Dólar (USD)</option>
                      </select>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label fw-semibold small ms-1">Impuesto / IVA (%)</label>
                      <input v-model.number="config.tax_percentage" type="number" class="form-control custom-input">
                    </div>
                  </div>
                </div>

                <div class="tab-pane fade" id="social">
                  <h5 class="mb-4 fw-bold text-dark">Presencia Digital</h5>
                  <div class="row g-4">
                    <div class="col-md-12">
                      <label class="form-label fw-semibold small ms-1">Facebook URL</label>
                      <div class="input-group">
                        <span class="input-group-text bg-white border-end-0" style="border-radius: 18px 0 0 18px;"><i class="bi bi-facebook text-primary"></i></span>
                        <input v-model="config.social_facebook" type="url" class="form-control custom-input border-start-0 ps-0" style="border-radius: 0 18px 18px 0;" placeholder="https://facebook.com/...">
                      </div>
                    </div>
                    <div class="col-md-12">
                      <label class="form-label fw-semibold small ms-1">Instagram URL</label>
                      <div class="input-group">
                        <span class="input-group-text bg-white border-end-0" style="border-radius: 18px 0 0 18px;"><i class="bi bi-instagram text-danger"></i></span>
                        <input v-model="config.social_instagram" type="url" class="form-control custom-input border-start-0 ps-0" style="border-radius: 0 18px 18px 0;" placeholder="https://instagram.com/...">
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Estilos adaptados a Kofán */
.verde-kofan {
  color: #0f3b2a !important;
}

.config-card {
  border-radius: 20px;
  overflow: hidden;
}

.sidebar-config {
  min-height: 400px;
}

.nav-pills .nav-link {
  color: #495057;
  border-radius: 12px;
  padding: 0.8rem 1rem;
  transition: all 0.2s ease;
}

/* Cambiamos el azul genérico de Bootstrap por el verde Kofán */
.nav-pills .nav-link.active {
  background-color: #0f3b2a;
  color: white;
}

.nav-pills .nav-link:hover:not(.active) {
  background-color: #e9ecef;
}

/* Estilo de inputs redondos como en el registro */
.custom-input {
  border-radius: 18px !important;
  padding: 0.6rem 1rem;
  font-size: 0.95rem;
  border-color: #dee2e6;
}

.custom-input:focus {
  border-color: #0f3b2a;
  box-shadow: 0 0 0 0.25rem rgba(15, 59, 42, 0.25);
}

/* Botón principal */
.btn-kofan {
  background-color: #0f3b2a !important;
  border-color: #0f3b2a !important;
  color: white !important;
  border-radius: 15px;
  transition: all 0.3s ease;
}

.btn-kofan:hover {
  background-color: #0a291d !important;
}

.btn-kofan:disabled {
  background-color: rgba(15, 59, 42, 0.65) !important;
  border-color: rgba(15, 59, 42, 0.65) !important;
}
</style>