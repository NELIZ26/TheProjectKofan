<script setup>
import { ref, onMounted, computed } from "vue"; 
import Swal from "sweetalert2";
import { createRoom, getRooms, deleteRoom, updateRoom, deleteRoomImage, addRoomImages } from "@/services/roomService";
import  ImageUploader from '@/components/ImageUploader.vue';
import  RoomCalendarModal from '@/components/RoomCalendarModal.vue';

// 🟢 BUENA PRÁCTICA: Centralizar la URL base. A futuro usa import.meta.env.VITE_API_URL
const API_BASE_URL = "http://127.0.0.1:8000";

const isLoading = ref(true);
const habitaciones = ref([]);
const isSubmitting = ref(false);
const uploaderRef = ref(null);

// 🟢 1. ESTADO UNIFICADO: Un solo formulario y una bandera para saber si editamos
const isEditing = ref(false);
const initialFormState = {
  room_number: "",
  name: "",
  price: "",
  capacity: 1,
  description: "",
  active: true,
  type: "",
  images: [] 
};
const roomForm = ref({ ...initialFormState });
const currentRoomId = ref(null); // Guarda el ID cuando estamos editando

// Variables para Múltiples Imágenes
const imagenesParaCargar = ref([]);
const isDragging = ref(false);
const fileInputRef = ref(null);
const closeBtnRef = ref(null); 
const modalVisible = ref(false);
const habitacionSeleccionada = ref(null);

const fotosRestantesCount = computed(() => {
  const fotosExistentes = roomForm.value.images ? roomForm.value.images.length : 0;
  return 5 - (fotosExistentes + imagenesParaCargar.value.length);
});

const cargarHabitaciones = async () => {
  isLoading.value = true;
  try {
    const response = await getRooms(); 
    habitaciones.value = response?.data && Array.isArray(response.data) ? response.data : 
                         Array.isArray(response) ? response : [];
  } catch (error) {
    console.error("Error al cargar habitaciones:", error);
  } finally {
    isLoading.value = false;
  }
};


onMounted(() => {
  cargarHabitaciones();
});

// --- LÓGICA DE DRAG & DROP UNIFICADA ---
const procesarArchivos = (files) => {
  if (!files || !files.length) return;
  if (files.length > fotosRestantesCount.value) {
    Swal.fire('Límite excedido', `Solo puedes subir ${fotosRestantesCount.value} foto(s) más.`, 'warning');
    return;
  }

  Array.from(files).forEach((file) => {
    if (!file.type.startsWith('image/')) {
      Swal.fire('Error', `El archivo '${file.name}' no es una imagen.`, 'error');
      return;
    }
    imagenesParaCargar.value.push({ file, previewUrl: URL.createObjectURL(file) });
  });
};

const handleFilesUpload = (event) => {
  procesarArchivos(event.target.files);
  event.target.value = ''; 
};

const onDrop = (event) => {
  isDragging.value = false;
  procesarArchivos(event.dataTransfer.files);
};

const triggerFileInput = () => {
  if (fotosRestantesCount.value > 0) fileInputRef.value.click();
};

const quitarFotoNueva = (index) => {
  URL.revokeObjectURL(imagenesParaCargar.value[index].previewUrl);
  imagenesParaCargar.value.splice(index, 1);
};

// --- PREPARACIÓN DE MODAL ---
const resetForm = () => {
  roomForm.value = { ...initialFormState };
  isEditing.value = false;
  currentRoomId.value = null;
  imagenesParaCargar.value = []; // Limpiamos nuestro array
  
  if (uploaderRef.value) {
    uploaderRef.value.reset(); // Le decimos al componente hijo que se limpie
  }
};

const prepararCreacion = () => resetForm();

const prepararEdicion = (hab) => {
  resetForm();
  isEditing.value = true;
  currentRoomId.value = hab.id || hab._id;
  roomForm.value = { ...hab }; // Clona los datos de la habitación al formulario
};

// --- GUARDAR O EDITAR (UNIFICADO) ---
const guardarHabitacion = async () => {
  const { room_number, name, price, type } = roomForm.value;

  if (!room_number || !name || !price || !type  || (!isEditing.value && imagenesParaCargar.value.length === 0)) {
    Swal.fire({ icon: "error", title: "Campos incompletos", text: "Verifica los datos y las fotos obligatorias." });
    return;
  }

  isSubmitting.value = true;
  try {
    const arrayDeArchivos = imagenesParaCargar.value;

    if (isEditing.value) {
      // Flujo de Edición
      await updateRoom(currentRoomId.value, roomForm.value);
      if (arrayDeArchivos.length > 0) {
        await addRoomImages(currentRoomId.value, arrayDeArchivos);
      }
      Swal.fire({ icon: "success", title: "¡Actualizada!", timer: 1500, showConfirmButton: false });
    } else {
      // Flujo de Creación
      await createRoom(roomForm.value, arrayDeArchivos);
      Swal.fire({ icon: "success", title: "¡Creada!", timer: 1500, showConfirmButton: false });
    }

    resetForm();
    await cargarHabitaciones();
    if (closeBtnRef.value) closeBtnRef.value.click(); // 🟢 Cerrar modal sin DOM puro

  } catch (error) {
    console.error("Error al guardar:", error);
    Swal.fire({ icon: "error", title: "Error", text: "Verifica los datos o tu conexión." });
  } finally {
    isSubmitting.value = false;
  }
};

// --- ELIMINAR REGISTROS ---
const eliminarHabitacion = async (id) => {
  const result = await Swal.fire({
    title: '¿Estás seguro?', text: "Esta acción es irreversible.", icon: 'warning',
    showCancelButton: true, confirmButtonColor: '#0f3b2a', cancelButtonColor: '#d33',
    confirmButtonText: 'Sí, eliminar', cancelButtonText: 'Cancelar'
  });

  if (result.isConfirmed) {
    try {
      await deleteRoom(id);
      Swal.fire({ icon: 'success', title: 'Eliminada', timer: 1500, showConfirmButton: false });
      await cargarHabitaciones(); 
    } catch (error) {
      Swal.fire('Error', 'No se pudo eliminar.', 'error');
    }
  }
};

const eliminarImagenExistente = async (index, imageUrl) => {
  const result = await Swal.fire({
    title: '¿Borrar esta foto?', text: "Se eliminará permanentemente.", icon: 'warning',
    showCancelButton: true, confirmButtonColor: '#d33', cancelButtonColor: '#0f3b2a',
    confirmButtonText: 'Sí, borrar', cancelButtonText: 'Cancelar'
  });

  if (result.isConfirmed) {
    try {
      await deleteRoomImage(currentRoomId.value, imageUrl);
      roomForm.value.images.splice(index, 1);
      Swal.fire({ icon: 'success', title: 'Foto eliminada', timer: 1500, showConfirmButton: false });
      await cargarHabitaciones(); 
    } catch (error) {
      Swal.fire('Error', 'No se pudo eliminar la foto', 'error');
    }
  }
};

const manejarErrorImagen = (e) => {
  e.target.src = 'https://via.placeholder.com/60x50?text=Sin+Foto';
};

const seleccionarPrincipal = (imgUrl) => {
  roomForm.value.main_image = imgUrl;
};

const abrirCalendario = (habitacion) => {
  habitacionSeleccionada.value = habitacion;
  modalVisible.value = true;
};

</script>

<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold text-dark mb-1">Gestión de Habitaciones</h2>
        <p class="text-muted mb-0">Administra y organiza la oferta de alojamiento de Kofán.</p>
      </div>
      
      <button @click="prepararNuevaHabitacion" class="btn btn-kofan shadow-sm px-4 py-2 rounded-pill" data-bs-toggle="modal" data-bs-target="#modalHabitacion">
        <font-awesome-icon icon="fa-solid fa-plus" class="me-2" />
        Nueva Habitación
      </button>
    </div>

    <div class="card border-0 shadow-sm rounded-4">
      <div class="table-responsive p-3">
        <table class="table table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th>Nombre</th>
              <th>Precio/Noche</th>
              <th>Capacidad</th>
              <th>Estado</th>
              <th class="text-center">Disponibilidad</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="habitaciones.length === 0 && !isLoading">
              <td colspan="5" class="text-center text-muted py-4">
                No hay habitaciones registradas
              </td>
            </tr>
            
            <tr v-for="hab in habitaciones" :key="hab.id || hab._id" class="align-middle">
              <td>
                <div class="d-flex align-items-center">
                  <img 
                    :src="`${API_BASE_URL}${hab.main_image}`" 
                    class="rounded me-3 border" 
                    style="width: 60px; height: 50px; object-fit: cover;"
                    @error="manejarErrorImagen"
                  >
                  <div>
                    <div class="fw-bold text-dark">{{ hab.name }}</div>
                    <small class="text-muted">N° {{ hab.room_number }}</small>
                  </div>
                </div>
              </td>

              <td class="fw-semibold text-dark">
                ${{ hab.price.toLocaleString('es-CO') }}
              </td>

              <td class="text-muted">
                {{ hab.capacity }} pers.
              </td>

              <td>
                <span :class="hab.active ? 'badge bg-success-subtle text-success px-3 py-2 rounded-pill' : 'badge bg-warning-subtle text-warning px-3 py-2 rounded-pill'">
                  {{ hab.active ? 'Activa' : 'Mantenimiento' }}
                </span>
              </td>

              <td class="text-center align-middle">
                <button @click="abrirCalendario(hab)" class="btn btn-sm btn-outline-primary rounded-pill px-3 shadow-sm">
                  <i class="fa fa-calendar-alt me-1"></i> Ver Fechas
                </button>
              </td>

              <td class="text-center align-middle">
                <div class="d-flex justify-content-center gap-2">
                  <button 
                    class="btn btn-light btn-sm border shadow-sm" 
                    data-bs-toggle="modal" 
                    data-bs-target="#modalHabitacion"
                    @click="prepararEdicion(hab)"
                    title="Editar habitación"
                  >
                    <font-awesome-icon :icon="['fas', 'pen-to-square']" style="color: #0f3b2a;" />
                  </button>
                  
                  <button 
                    class="btn btn-light btn-sm border shadow-sm" 
                    @click="eliminarHabitacion(hab.id || hab._id)"
                    title="Eliminar habitación"
                  >
                    <font-awesome-icon :icon="['fas', 'trash']" class="text-danger" />
                  </button>
                </div>
              </td>
            </tr>        
          </tbody>
        </table>
      </div>
    </div>

    <div class="modal fade" id="modalHabitacion" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header bg-dark text-white border-0">
            <h5 class="modal-title fw-bold">
              <font-awesome-icon :icon="isEditing ? 'fa-solid fa-pen-to-square' : 'fa-solid fa-bed'" class="me-2" />
              {{ isEditing ? 'Editar Habitación' : 'Registrar Habitación' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" @click="resetForm"></button>
          </div>

          <form @submit.prevent="guardarHabitacion">
            <div class="modal-body p-4">
              <div class="row g-3">
                
                <div class="col-md-4">
                  <label class="form-label fw-bold">N° Habitación</label>
                  <input v-model="roomForm.room_number" type="text" class="form-control" required />
                </div>
                
                <div class="col-md-8">
                  <label class="form-label fw-bold">Nombre</label>
                  <input v-model="roomForm.name" type="text" class="form-control" required />
                </div>
                
                <div class="col-md-6">
                  <label class="form-label fw-bold">Precio</label>
                  <input v-model="roomForm.price" type="number" class="form-control" required />
                </div>
                
                <div class="col-md-6">
                  <label class="form-label fw-bold">Capacidad</label>
                  <input v-model="roomForm.capacity" type="number" class="form-control" required />
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-bold">Tipo de Alojamiento</label>
                  <select v-model="roomForm.type" class="form-select" required>
                  <option value="" disabled>Selecciona una opción...</option>
                  <option value="cabana">Cabaña Independiente</option>
                  <option value="habitacion">Habitación en Maloka</option>
                  </select>
                 </div>

                <div class="col-12" v-if="isEditing">
                  <label class="form-label fw-bold">Estado Operativo</label>
                  <select class="form-select" v-model="roomForm.active">
                    <option :value="true">Activa (Lista para reservas)</option>
                    <option :value="false">En Mantenimiento (Bloqueada)</option>
                  </select>
                </div>
                
                <div class="col-12">
                  <label class="form-label fw-bold">Descripción / Amenidades</label>
                  <textarea v-model="roomForm.description" class="form-control" rows="2"></textarea>
                </div>

                <div class="col-12 mt-4" v-if="isEditing && roomForm.images && roomForm.images.length">
                  <label class="form-label fw-bold mb-1">Fotos Actuales de la Cabaña</label>
                  <p class="text-muted small mb-3">Haz clic en la <font-awesome-icon :icon="['fas', 'star']" class="text-success" /> para elegir la foto principal.</p>
                  
                  <div class="row g-2">
                    <div v-for="(imgUrl, index) in roomForm.images" :key="index" class="col-4 col-md-3">
                      <div 
                        class="card h-100 p-1 position-relative border transition-all photo-card"
                        :class="{ 'border-success border-2 shadow principal-highlight': imgUrl === roomForm.main_image }"
                      >
                        <span v-if="imgUrl === roomForm.main_image" class="position-absolute principal-badge rounded-pill bg-success text-white shadow-sm">
                          Principal
                        </span>

                        <img :src="`${API_BASE_URL}${imgUrl}`" class="rounded object-fit-cover w-100" style="height: 90px;">

                        <button 
                          type="button" 
                          class="btn btn-danger btn-sm position-absolute rounded-pill action-btn btn-trash shadow" 
                          @click.stop="eliminarImagenExistente(index, imgUrl)"
                          title="Eliminar foto"
                        >
                          <font-awesome-icon :icon="['fas', 'trash']" style="font-size: 0.70rem;" />
                        </button>

                        <button 
                          v-if="imgUrl !== roomForm.main_image"
                          type="button" 
                          class="btn btn-light btn-sm position-absolute rounded-pill action-btn btn-star shadow" 
                          @click.stop="seleccionarPrincipal(imgUrl)"
                          title="Hacer foto principal"
                        >
                          <font-awesome-icon :icon="['fas', 'star']" class="text-success" style="font-size: 0.70rem;" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="col-12 mt-3">
                <ImageUploader 
                  ref="uploaderRef"
                  v-model="imagenesParaCargar"
                  :existing-count="roomForm.images ? roomForm.images.length : 0"
                  :is-editing="isEditing"
                />
              </div>

              </div>
            </div>

            <div class="modal-footer border-0 p-4 pt-0">
              <button type="button" class="btn btn-light px-4" data-bs-dismiss="modal" ref="closeBtnRef" @click="resetForm">
                Cancelar
              </button>
              <button type="submit" class="btn btn-kofan px-4" :disabled="isSubmitting">
                {{ isSubmitting ? 'Guardando...' : (isEditing ? 'Guardar Cambios' : 'Guardar Habitación') }}
              </button>
            </div>
          </form>

        </div>
      </div>
    </div>

    <RoomCalendarModal 
    :show="modalVisible" 
    :habitacion="habitacionSeleccionada"
    @close="modalVisible = false"
    @reservaCreada="cargarHabitaciones" 
    />
  </div>
</template>

<style scoped>
/* Tus estilos se mantienen intactos */
.btn-kofan {
  background-color: #0f3b2a;
  color: white;
  border-radius: 10px;
  font-weight: 500;
  transition: 0.3s;
}
.btn-kofan:hover {
  background-color: #1a5c43;
  color: white;
  transform: translateY(-2px);
}
.border-dashed {
  border-style: dashed !important;
}

/* 🟢 Estilos para las Fotos Actuales */
.photo-card {
  overflow: hidden;
}

.principal-highlight {
  background-color: #f0fdf4; /* Fondo verde clarito */
}

.principal-badge {
  top: -6px; 
  left: -6px; 
  font-size: 0.65rem; 
  font-weight: 700; 
  padding: 3px 8px; 
  z-index: 5;
}

.action-btn {
  bottom: 8px; 
  opacity: 0; 
  transform: scale(0.8); 
  width: 28px; height: 28px; padding: 0; display: flex; align-items: center; justify-content: center; z-index: 10;
  transition: all 0.2s ease-in-out;
}

.btn-trash { right: 8px; }
.btn-star { right: 42px; } 

.photo-card:hover .action-btn {
  opacity: 1;
  transform: scale(1);
}

</style>