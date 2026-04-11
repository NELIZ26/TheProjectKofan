<script setup>
import { ref, onMounted } from 'vue';
import { fetchConfig, saveConfig, uploadLogo } from '@/services/configService';
import defaultLogo from '@/img/Kofan.png';

const isLoading = ref(true);
const isSaving = ref(false);
const message = ref({ text: '', type: '' });
const fileInput = ref(null);

const base = import.meta.env.VITE_API_URL || "http://localhost:8000";

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
  social_tiktok: "",
  whatsapp_number: "",
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
    message.value = { text: 'Perfecto, la imagen del hotel ya está actualizada.', type: 'success' };
  } catch (error) {
    message.value = { text: 'No pudimos actualizar la imagen por ahora. Inténtalo nuevamente.', type: 'danger' };
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
    message.value = { text: 'Listo 🌿 Los cambios quedaron guardados correctamente.', type: 'success' };
  } catch (error) {
    message.value = { text: 'No pudimos guardar por ahora. Tus datos siguen seguros; intentemos nuevamente.', type: 'danger' };
  } finally {
    isSaving.value = false;
    setTimeout(() => message.value.text = '', 3500);
  }
};

onMounted(loadSettings);
</script>

<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
      <div>
        <p class="brand-handmade mb-1">Detalles que acompañan cada bienvenida</p>
        <h2 class="fw-bold section-title text-kofan mb-0"><font-awesome-icon icon="fa-solid fa-hotel" class="me-2" />Configuración del Hotel</h2>
      </div>
      <button 
        @click="handleSave" 
        class="btn btn-kofan px-4 shadow-sm" 
        :disabled="isSaving || isLoading"
      >
        <span v-if="isSaving" class="spinner-border spinner-border-sm me-2"></span>
        <font-awesome-icon v-else icon="fa-solid fa-circle-check" class="me-2" />
        Guardar cambios del hotel
      </button>
    </div>

    <div v-if="message.text" :class="['alert alert-dismissible fade show shadow-sm alert-handmade', `alert-${message.type}`]" style="border-radius: 12px;">
      {{ message.text }}
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border verde-kofan" role="status"></div>
      <p class="mt-2 text-muted brand-handmade">Preparando los detalles del hotel...</p>
    </div>

    <div v-else class="card config-card eco-card shadow-sm border-0">
      <div class="card-body p-0">
        <div class="row g-0">
          <div class="col-md-3 border-end bg-light p-3 sidebar-config">
            <div class="nav flex-column nav-pills" id="v-pills-tab" role="tablist">
              <button class="nav-link active text-start mb-2" data-bs-toggle="pill" data-bs-target="#general">
                <font-awesome-icon icon="fa-solid fa-circle-info" class="me-2" />Esencia del hotel
              </button>
              <button class="nav-link text-start mb-2" data-bs-toggle="pill" data-bs-target="#hotel">
                <font-awesome-icon icon="fa-solid fa-hotel" class="me-2" />Operación diaria
              </button>
              <button class="nav-link text-start mb-2" data-bs-toggle="pill" data-bs-target="#social">
                <font-awesome-icon icon="fa-solid fa-share-nodes" class="me-2" />Canales de contacto
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
                        :src="config.logo_url ? `${base}${config.logo_url}` : defaultLogo" 
                        alt="Logo Preview" 
                        class="img-thumbnail shadow-sm p-2"
                        style="max-height: 120px; border-radius: 15px;"
                      >
                      </div>
                      <input type="file" ref="fileInput" @change="handleLogoUpload" class="d-none" accept="image/*">
                      <button type="button" class="btn btn-outline-secondary btn-sm" style="border-radius: 10px;" @click="fileInput.click()">
                        <font-awesome-icon icon="fa-solid fa-camera" class="me-2" />Cambiar Logo
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
                      <div class="position-relative">
                        <font-awesome-icon :icon="['fab', 'facebook-f']" class="text-primary position-absolute top-50 translate-middle-y ms-3 fs-5" />
                        <input v-model="config.social_facebook" type="url" class="form-control custom-input ps-5 py-2" style="border-radius: 12px;" placeholder="https://facebook.com/...">
                      </div>
                    </div>
                    
                    <div class="col-md-12">
                      <label class="form-label fw-semibold small ms-1">Instagram URL</label>
                      <div class="position-relative">
                        <font-awesome-icon :icon="['fab', 'instagram']" class="text-danger position-absolute top-50 translate-middle-y ms-3 fs-5" />
                        <input v-model="config.social_instagram" type="url" class="form-control custom-input ps-5 py-2" style="border-radius: 12px;" placeholder="https://instagram.com/...">
                      </div>
                    </div>
                    
                    <div class="col-md-12">
                      <label class="form-label fw-semibold small ms-1">TikTok URL</label>
                      <div class="position-relative">
                        <font-awesome-icon :icon="['fab', 'tiktok']" class="text-dark position-absolute top-50 translate-middle-y ms-3 fs-5" />
                        <input v-model="config.social_tiktok" type="url" class="form-control custom-input ps-5 py-2" style="border-radius: 12px;" placeholder="https://tiktok.com/@...">
                      </div>
                    </div>

                    <div class="col-md-12">
                      <label class="form-label fw-semibold small ms-1">Número de WhatsApp</label>
                      <div class="position-relative">
                        <font-awesome-icon :icon="['fab', 'whatsapp']" class="text-success position-absolute top-50 translate-middle-y ms-3 fs-5" />
                        <input v-model="config.whatsapp_number" type="text" class="form-control custom-input ps-5 py-2" style="border-radius: 12px;" placeholder="Ej: 573224225925">
                      </div>
                      <div class="form-text small ms-2 mt-1 opacity-75">
                        Incluye el indicativo (ej. 57 para Colombia) sin el símbolo "+".
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
.verde-kofan {
  color: var(--k-forest) !important;
}

.config-card {
  border-radius: 20px;
  overflow: hidden;
}

.sidebar-config {
  min-height: 400px;
  background: linear-gradient(180deg, #f8fcfe 0%, var(--k-forest-soft) 100%);
}
 
.nav-pills .nav-link {
  color: var(--k-text);
  border-radius: 14px;
  padding: 0.8rem 1rem;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.nav-pills .nav-link.active {
  background-color: rgba(139, 207, 91, 0.22);
  color: var(--k-forest);
  border-color: rgba(139, 207, 91, 0.45);
}

.nav-pills .nav-link:hover:not(.active) {
  background-color: rgba(255, 255, 255, 0.75);
  border-color: #d6edf7;
}

.custom-input {
  border-radius: 18px !important;
  padding: 0.65rem 1rem;
  font-size: 0.95rem;
  border-color: var(--k-border);
  background: rgba(255, 255, 255, 0.95);
}

.custom-input:focus {
  border-color: var(--k-sky-strong);
  box-shadow: 0 0 0 0.25rem rgba(143, 211, 255, 0.28);
}

.btn-kofan:disabled {
  background-color: rgba(139, 207, 91, 0.55) !important;
  border-color: rgba(139, 207, 91, 0.55) !important;
}
</style>