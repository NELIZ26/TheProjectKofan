<script setup>
import { ref, onMounted, computed } from "vue"; 
import Swal from "sweetalert2";
import { createRoom, getRooms, deleteRoom, updateRoom, deleteRoomImage, addRoomImages } from "@/services/roomService";
import  ImageUploader from '@/components/ImageUploader.vue';
import  RoomCalendarModal from '@/components/RoomCalendarModal.vue';

const API_BASE_URL = "http://127.0.0.1:8000";
const isLoading = ref(true);
const habitaciones = ref([]);
const isSubmitting = ref(false);
const uploaderRef = ref(null);
const isEditing = ref(false);

// 🟢 1. AGREGAMOS LOS DOS CAMPOS NUEVOS AL ESTADO INICIAL
const initialFormState = {
  room_number: "",
  name: "",
  price: "",
  capacity: 1,
  description: "",
  active: true,
  type: "",
  num_cuartos: 1, // Nuevo: Nivel de privacidad
  tipo_camas: "", // Nuevo: Distribución (Ej: 1 Doble, 2 Sencillas)
  amenities: [],
  images: [] 
};

const roomForm = ref({ ...initialFormState });
const currentRoomId = ref(null);
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

const resetForm = () => {
  roomForm.value = { ...initialFormState };
  isEditing.value = false;
  currentRoomId.value = null;
  imagenesParaCargar.value = []; 
  
  if (uploaderRef.value) {
    uploaderRef.value.reset();
  }
};

const prepararCreacion = () => resetForm();

const prepararEdicion = (hab) => {
  resetForm();
  isEditing.value = true;
  currentRoomId.value = hab.id || hab._id;
  roomForm.value = { ...hab };
};

const guardarHabitacion = async () => {
  // 🟢 2. VALIDAMOS QUE EL CAMPO DE CAMAS SE LLENE
  const { room_number, name, price, type, tipo_camas } = roomForm.value;

  if (!room_number || !name || !price || !type || !tipo_camas || (!isEditing.value && imagenesParaCargar.value.length === 0)) {
    Swal.fire({ icon: "error", title: "Campos incompletos", text: "Verifica los datos obligatorios, incluyendo la distribución de camas." });
    return;
  }

  isSubmitting.value = true;
  try {
    const arrayDeArchivos = imagenesParaCargar.value;

    if (isEditing.value) {
      await updateRoom(currentRoomId.value, roomForm.value);
      if (arrayDeArchivos.length > 0) {
        await addRoomImages(currentRoomId.value, arrayDeArchivos);
      }
      Swal.fire({ icon: "success", title: "¡Actualizada!", timer: 1500, showConfirmButton: false });
    } else {
      await createRoom(roomForm.value, arrayDeArchivos);
      Swal.fire({ icon: "success", title: "¡Creada!", timer: 1500, showConfirmButton: false });
    }

    resetForm();
    await cargarHabitaciones();
    if (closeBtnRef.value) closeBtnRef.value.click();

  } catch (error) {
    console.error("Error al guardar:", error);
    Swal.fire({ icon: "error", title: "Error", text: "Verifica los datos o tu conexión." });
  } finally {
    isSubmitting.value = false;
  }
};

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
  // Rompemos el bucle
  e.target.onerror = null; 
  
  // Asignamos una imagen en código Base64 (un pequeño rectángulo gris)
  e.target.src = 'data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%2260%22%20height%3D%2250%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2060%2050%22%20preserveAspectRatio%3D%22none%22%3E%3Crect%20width%3D%2260%22%20height%3D%2250%22%20fill%3D%22%23eeeeee%22%2F%3E%3Ctext%20text-anchor%3D%22middle%22%20x%3D%2230%22%20y%3D%2230%22%20style%3D%22fill%3A%23aaaaaa%3Bfont-weight%3Abold%3Bfont-size%3A10px%3Bfont-family%3AArial%2CHelvetica%2Csans-serif%22%3ESin%20Foto%3C%2Ftext%3E%3C%2Fsvg%3E';
};

const seleccionarPrincipal = (imgUrl) => {
  roomForm.value.main_image = imgUrl;
};

const abrirCalendario = (habitacion) => {
  habitacionSeleccionada.value = habitacion;
  modalVisible.value = true;
};

const listaAmenidades = [
  "Aire Acondicionado",
  "Ventilador",
  "Televisión",
  "Wifi",
  "Baño Privado",
  "Nevera / Minibar",
  "Zonas Verdes",
  "Vista a la Selva",
  "Malla Catamarán",
  "Tina / Jacuzzi",
  "Balcón"
];
</script>

<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold text-dark mb-1">Gestión de Habitaciones</h2>
        <p class="text-muted mb-0">Administra y organiza la oferta de alojamiento de Kofán.</p>
      </div>
      
      <button @click="prepararCreacion" class="btn btn-dark shadow-sm rounded-pill px-4" data-bs-toggle="modal" data-bs-target="#modalHabitacion">
        <i class="bi bi-plus-circle-fill me-2"></i>
        Nueva Habitación
      </button>
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="table-responsive p-0">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th class="ps-4 py-3 text-muted small fw-bold">NOMBRE</th>
              <th class="py-3 text-muted small fw-bold">PRECIO/NOCHE</th>
              <th class="py-3 text-muted small fw-bold">CAPACIDAD</th>
              <th class="py-3 text-muted small fw-bold">ESTADO</th>
              <th class="text-center py-3 text-muted small fw-bold">DISPONIBILIDAD</th>
              <th class="text-center py-3 text-muted small fw-bold">ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="habitaciones.length === 0 && !isLoading">
              <td colspan="6" class="text-center text-muted py-5">
                <i class="bi bi-door-closed display-4 mb-3 d-block text-light"></i>
                No hay habitaciones registradas
              </td>
            </tr>
            
            <tr v-for="hab in habitaciones" :key="hab.id || hab._id" class="align-middle">
              <td class="ps-4">
                <div class="d-flex align-items-center">
                  <img 
                    :src="`${API_BASE_URL}${hab.main_image}`" 
                    class="rounded me-3 border shadow-sm" 
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
                <span :class="hab.active ? 'badge bg-success bg-opacity-10 text-success border border-success px-3 py-2 rounded-pill' : 'badge bg-warning bg-opacity-10 text-warning border border-warning px-3 py-2 rounded-pill'">
                  <i :class="hab.active ? 'bi bi-check-circle-fill' : 'bi bi-tools'" class="me-1"></i>
                  {{ hab.active ? 'Activa' : 'Mantenimiento' }}
                </span>
              </td>

              <td class="text-center align-middle">
                <button @click="abrirCalendario(hab)" class="btn btn-sm btn-outline-primary rounded-pill px-3 fw-medium shadow-sm" style="font-size: 0.82rem;">
                  <i class="bi bi-calendar-range me-1"></i> Ver Fechas
                </button>
              </td>

              <td class="text-center align-middle">
                <div class="d-flex justify-content-center gap-2">
                  
                  <button 
                    class="btn btn-sm btn-outline-dark rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                    style="width: 35px; height: 35px;"
                    data-bs-toggle="modal" 
                    data-bs-target="#modalHabitacion"
                    @click="prepararEdicion(hab)"
                    title="Editar habitación"
                  >
                    <i class="bi bi-pencil-square fs-6"></i>
                  </button>
                  
                  <button 
                    class="btn btn-sm btn-outline-danger rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                    style="width: 35px; height: 35px;"
                    @click="eliminarHabitacion(hab.id || hab._id)"
                    title="Eliminar habitación"
                  >
                    <i class="bi bi-trash fs-6"></i>
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
              <i :class="isEditing ? 'bi bi-pencil-square' : 'bi bi-door-open-fill'" class="me-2"></i>
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
                  <label class="form-label fw-bold">Capacidad Total (Pers.)</label>
                  <input v-model="roomForm.capacity" type="number" min="1" class="form-control" required />
                </div>

                <div class="col-md-6">
                <label class="form-label fw-bold">Tipo de Alojamiento</label>
                <select v-model="roomForm.type" class="form-select" required>
                  <option value="" disabled>Selecciona una opción...</option>
                  <option value="individual">Habitación Individual</option>
                  <option value="family">Habitación Familiar</option>
                  <option value="cabins">Cabaña Independiente</option>
                </select>
              </div>

                <div class="col-md-6">
                  <label class="form-label fw-bold">N° de Habitaciones (Cuartos)</label>
                  <input v-model="roomForm.num_cuartos" type="number" min="1" class="form-control" required />
                </div>

                <div class="col-12 mt-3">
                  <label class="form-label fw-bold">Distribución de Camas</label>
                  <input v-model="roomForm.tipo_camas" type="text" class="form-control" placeholder="Ej: 1 Cama Doble, 2 Sencillas" required />
                  <small class="text-muted">Este texto es el que verá el cliente en la tarjeta principal.</small>
                </div>

                <div class="col-12 mt-3" v-if="isEditing">
                  <label class="form-label fw-bold">Estado Operativo</label>
                  <select class="form-select" v-model="roomForm.active">
                    <option :value="true">Activa (Lista para reservas)</option>
                    <option :value="false">En Mantenimiento (Bloqueada)</option>
                  </select>
                </div>
                
                <div class="col-12 mt-3">
                  <label class="form-label fw-bold">Descripción de la Habitación</label>
                  <textarea v-model="roomForm.description" class="form-control border-light-subtle shadow-sm" rows="2" placeholder="Ej: Cabaña romántica ideal para parejas..."></textarea>
                </div>

                <div class="col-12 mt-4">
                  <label class="form-label fw-bold mb-3 border-bottom pb-2 w-100">¿Qué incluye la habitación? (Amenidades)</label>
                  <div class="row g-2">
                    <div class="col-md-4 col-sm-6" v-for="(amenidad, index) in listaAmenidades" :key="index">
                      <div class="form-check form-switch p-2 rounded bg-light border border-light-subtle transition-all" 
                           :class="{ 'border-success bg-success-subtle': roomForm.amenities && roomForm.amenities.includes(amenidad) }">
                        <input class="form-check-input ms-1 me-2" type="checkbox" role="switch" :id="'amenidad-' + index" :value="amenidad" v-model="roomForm.amenities">
                        <label class="form-check-label text-dark" :for="'amenidad-' + index" style="cursor: pointer;">
                          {{ amenidad }}
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="col-12 mt-4" v-if="isEditing && roomForm.images && roomForm.images.length">
                  <label class="form-label fw-bold mb-1">Fotos Actuales de la Cabaña</label>
                  <p class="text-muted small mb-3">Haz clic en la <i class="bi bi-star-fill text-warning"></i> para elegir la foto principal.</p>
                  
                  <div class="row g-2">
                    <div v-for="(imgUrl, index) in roomForm.images" :key="index" class="col-4 col-md-3">
                      <div 
                        class="card h-100 p-1 position-relative border transition-all photo-card"
                        :class="{ 'border-success border-2 shadow principal-highlight': imgUrl === roomForm.main_image }"
                      >
                        <span v-if="imgUrl === roomForm.main_image" class="position-absolute principal-badge rounded-pill bg-success text-white shadow-sm px-2" style="top: -5px; left: -5px; font-size: 0.75rem; z-index: 2;">
                          Principal
                        </span>

                        <img :src="`${API_BASE_URL}${imgUrl}`" class="rounded object-fit-cover w-100" style="height: 90px;">

                        <button 
                          type="button" 
                          class="btn btn-danger btn-sm position-absolute rounded-circle d-inline-flex align-items-center justify-content-center shadow" 
                          style="width: 28px; height: 28px; bottom: 5px; right: 5px;"
                          @click.stop="eliminarImagenExistente(index, imgUrl)"
                          title="Eliminar foto"
                        >
                          <i class="bi bi-trash-fill" style="font-size: 0.8rem;"></i>
                        </button>

                        <button 
                          v-if="imgUrl !== roomForm.main_image"
                          type="button" 
                          class="btn btn-light btn-sm position-absolute rounded-circle d-inline-flex align-items-center justify-content-center shadow" 
                          style="width: 28px; height: 28px; bottom: 5px; left: 5px;"
                          @click.stop="seleccionarPrincipal(imgUrl)"
                          title="Hacer foto principal"
                        >
                          <i class="bi bi-star-fill text-warning" style="font-size: 0.8rem;"></i>
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
              <button type="button" class="btn btn-light border px-4 rounded-pill" data-bs-dismiss="modal" ref="closeBtnRef" @click="resetForm">
                Cancelar
              </button>
              <button type="submit" class="btn btn-dark px-4 rounded-pill shadow-sm" :disabled="isSubmitting">
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