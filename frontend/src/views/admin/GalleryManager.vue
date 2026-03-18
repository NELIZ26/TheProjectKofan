<template>
  <div class="gallery-manager">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold verde-kofan mb-0">Gestión de Galería</h3>
        <p class="text-muted small mb-0">Administra las fotos públicas del Ecohotel</p>
      </div>
      <button class="btn btn-kofan px-4" @click="mostrarFormulario = true">
        <font-awesome-icon :icon="['fas', 'plus']" class="me-2" />
        Subir Foto
      </button>
    </div>

    <!-- Formulario de subida -->
    <div v-if="mostrarFormulario" class="upload-card mb-4 p-4 shadow-sm">
      <h5 class="fw-bold verde-kofan mb-3">Nueva Foto</h5>
      <div class="row g-3">

        <div class="col-md-6">
          <label class="form-label fw-semibold small">Título</label>
          <input v-model="nuevaFoto.titulo" type="text" class="form-control kofan-input" placeholder="Ej: Atardecer en el río">
        </div>

        <div class="col-md-6">
          <label class="form-label fw-semibold small">Categoría</label>
          <select v-model="nuevaFoto.categoria" class="form-select kofan-input">
            <option value="">Seleccione...</option>
            <option v-for="cat in categorias" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
          </select>
        </div>

        <div class="col-12">
          <label class="form-label fw-semibold small">Imagen</label>
          <div
            class="drop-zone"
            :class="{ 'drag-over': isDragging }"
            @dragover.prevent="isDragging = true"
            @dragleave="isDragging = false"
            @drop.prevent="onDrop"
            @click="$refs.fileInput.click()"
          >
            <div v-if="!preview">
              <font-awesome-icon :icon="['fas', 'cloud-arrow-up']" class="fs-2 text-muted mb-2 d-block mx-auto" />
              <p class="text-muted small mb-0">Arrastra una imagen o haz clic para seleccionar</p>
              <p class="text-muted" style="font-size:0.75rem">JPEG, PNG, WebP — máx. 5MB</p>
            </div>
            <img v-else :src="preview" class="preview-img" alt="Preview" />
          </div>
          <input ref="fileInput" type="file" accept="image/*" class="d-none" @change="onFileSelect">
        </div>

      </div>

      <div class="d-flex gap-2 mt-3 justify-content-end">
        <button class="btn btn-outline-secondary" @click="cancelarUpload">Cancelar</button>
        <button class="btn btn-kofan px-4" @click="subirFoto" :disabled="isUploading">
          <span v-if="isUploading" class="spinner-border spinner-border-sm me-2"></span>
          {{ isUploading ? 'Subiendo...' : 'Guardar Foto' }}
        </button>
      </div>
    </div>

    <!-- Filtros -->
    <div class="d-flex gap-2 flex-wrap mb-4">
      <button
        v-for="cat in [{ value: 'todos', label: 'Todas' }, ...categorias]"
        :key="cat.value"
        class="btn btn-sm"
        :class="filtroActivo === cat.value ? 'btn-kofan' : 'btn-outline-kofan'"
        @click="cambiarFiltro(cat.value)"
      >
        {{ cat.label }}
        <span v-if="filtroActivo === cat.value" class="ms-1 badge bg-white text-success">
          {{ fotos.length }}
        </span>
      </button>
    </div>

    <!-- Estado de carga -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-success" role="status"></div>
      <p class="text-muted mt-2 small">Cargando galería...</p>
    </div>

    <!-- Sin fotos -->
    <div v-else-if="fotos.length === 0" class="empty-state text-center py-5">
      <font-awesome-icon :icon="['fas', 'images']" class="fs-1 text-muted mb-3 d-block mx-auto" />
      <p class="text-muted">No hay fotos en esta categoría.</p>
      <button class="btn btn-kofan mt-2" @click="mostrarFormulario = true">Subir primera foto</button>
    </div>

    <!-- Grid de fotos -->
    <div v-else class="gallery-grid">
      <div v-for="foto in fotos" :key="foto.id" class="gallery-item">
        <img :src="fotoUrl(foto.url)" :alt="foto.titulo" class="gallery-img" />
        <div class="gallery-overlay">
          <span class="foto-titulo">{{ foto.titulo }}</span>
          <span class="foto-categoria badge-cat">{{ labelCategoria(foto.categoria) }}</span>
          <button class="btn btn-danger btn-sm mt-2" @click="confirmarEliminar(foto)" :disabled="eliminando === foto.id">
            <span v-if="eliminando === foto.id" class="spinner-border spinner-border-sm"></span>
            <font-awesome-icon v-else :icon="['fas', 'trash']" />
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";

const fotos = ref([]);
const isLoading = ref(false);
const isUploading = ref(false);
const eliminando = ref(null);
const mostrarFormulario = ref(false);
const filtroActivo = ref("todos");
const isDragging = ref(false);
const preview = ref(null);
const fileInput = ref(null);

const nuevaFoto = ref({ titulo: "", categoria: "", archivo: null });

const categorias = [
  { value: "naturaleza",    label: "Naturaleza" },
  { value: "experiencias",  label: "Experiencias" },
  { value: "instalaciones", label: "Instalaciones" },
  { value: "eventos",       label: "Eventos" },
];

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const fotoUrl = (url) => `${BASE_URL}${url}`;

const labelCategoria = (val) => categorias.find(c => c.value === val)?.label || val;

const cargarFotos = async (categoria = "todos") => {
  isLoading.value = true;
  try {
    const params = categoria !== "todos" ? `?categoria=${categoria}` : "";
    const { data } = await apiClient.get(`/gallery/${params}`);
    fotos.value = data;
  } catch {
    Swal.fire({ icon: "error", title: "Error", text: "No se pudieron cargar las fotos.", confirmButtonColor: "#0f3b2a" });
  } finally {
    isLoading.value = false;
  }
};

const cambiarFiltro = (cat) => {
  filtroActivo.value = cat;
  cargarFotos(cat);
};

const onFileSelect = (e) => {
  const file = e.target.files[0];
  if (file) setArchivo(file);
};

const onDrop = (e) => {
  isDragging.value = false;
  const file = e.dataTransfer.files[0];
  if (file) setArchivo(file);
};

const setArchivo = (file) => {
  nuevaFoto.value.archivo = file;
  const reader = new FileReader();
  reader.onload = (e) => { preview.value = e.target.result; };
  reader.readAsDataURL(file);
};

const cancelarUpload = () => {
  mostrarFormulario.value = false;
  nuevaFoto.value = { titulo: "", categoria: "", archivo: null };
  preview.value = null;
};

const subirFoto = async () => {
  const { titulo, categoria, archivo } = nuevaFoto.value;

  if (!titulo || !categoria || !archivo) {
    return Swal.fire({ icon: "warning", title: "Campos incompletos", text: "Completa todos los campos y selecciona una imagen.", confirmButtonColor: "#0f3b2a" });
  }

  isUploading.value = true;

  try {
    const formData = new FormData();
    formData.append("file", archivo);
    formData.append("titulo", titulo);
    formData.append("categoria", categoria);

    await apiClient.post("/gallery/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    await Swal.fire({ icon: "success", title: "¡Foto subida!", timer: 1500, showConfirmButton: false });
    cancelarUpload();
    cargarFotos(filtroActivo.value);

  } catch (error) {
    const detail = error.response?.data?.detail || "No se pudo subir la foto.";
    Swal.fire({ icon: "error", title: "Error al subir", text: detail, confirmButtonColor: "#0f3b2a" });
  } finally {
    isUploading.value = false;
  }
};

const confirmarEliminar = async (foto) => {
  const result = await Swal.fire({
    title: "¿Eliminar foto?",
    text: `Se eliminará "${foto.titulo}" permanentemente.`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#dc3545",
    cancelButtonColor: "#6c757d",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  });

  if (!result.isConfirmed) return;

  eliminando.value = foto.id;
  try {
    await apiClient.delete(`/gallery/${foto.id}`);
    fotos.value = fotos.value.filter(f => f.id !== foto.id);
    Swal.fire({ icon: "success", title: "Foto eliminada", timer: 1500, showConfirmButton: false });
  } catch {
    Swal.fire({ icon: "error", title: "Error", text: "No se pudo eliminar la foto.", confirmButtonColor: "#0f3b2a" });
  } finally {
    eliminando.value = null;
  }
};

onMounted(() => cargarFotos());
</script>

<style scoped>
.verde-kofan { color: #0f3b2a; }

.upload-card {
  background: #fff;
  border-radius: 20px;
  border: 1px solid #e0e0e0;
}

.kofan-input {
  border-radius: 10px;
  border: 1px solid #e0e0e0;
  padding: 10px 15px;
  background: #fdfdfd;
}

.kofan-input:focus {
  border-color: #0f3b2a;
  box-shadow: 0 0 0 0.2rem rgba(15, 59, 42, 0.1);
}

.drop-zone {
  border: 2px dashed #c8e6c9;
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f9fdf9;
  min-height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.drop-zone.drag-over {
  border-color: #0f3b2a;
  background: #f0fdf4;
}

.preview-img {
  max-height: 160px;
  border-radius: 10px;
  object-fit: cover;
}

.btn-kofan {
  background-color: #0f3b2a;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-kofan:hover:not(:disabled) {
  background-color: #1a5c43;
  transform: translateY(-1px);
}

.btn-kofan:disabled { opacity: 0.7; cursor: not-allowed; }

.btn-outline-kofan {
  border: 1px solid #0f3b2a;
  color: #0f3b2a;
  background: transparent;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-outline-kofan:hover {
  background: #f0fdf4;
}

/* Grid de fotos */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.gallery-item {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 4/3;
  background: #f0f0f0;
  cursor: pointer;
}

.gallery-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.gallery-item:hover .gallery-img {
  transform: scale(1.08);
}

.gallery-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(transparent 30%, rgba(15, 59, 42, 0.92));
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 14px;
  opacity: 0;
  transition: opacity 0.3s;
}

.gallery-item:hover .gallery-overlay {
  opacity: 1;
}

.foto-titulo {
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  line-height: 1.2;
}

.badge-cat {
  background: rgba(255,255,255,0.2);
  color: #c8e6c9;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 20px;
  margin-top: 4px;
  display: inline-block;
}

.empty-state .fa-images { color: #ccc; }
</style>