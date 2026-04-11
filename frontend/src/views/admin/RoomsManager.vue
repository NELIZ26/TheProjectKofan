<script setup>
import { ref, onMounted, computed } from "vue"; 
import Swal from "sweetalert2";
import { createRoom, getRooms, deleteRoom, updateRoom, deleteRoomImage, addRoomImages } from "@/services/roomService";
import  ImageUploader from '@/components/ImageUploader.vue';
import  RoomCalendarModal from '@/components/RoomCalendarModal.vue';

const API_BASE_URL = "http://127.0.0.1:8000";
const isLoading = ref(true);
const habitaciones = ref([]);
const roomFilter = ref("all");
const isSubmitting = ref(false);

const habitacionesFiltradas = computed(() => {
  if (roomFilter.value === "available") {
    return habitaciones.value.filter((hab) => hab.active);
  }

  if (roomFilter.value === "maintenance") {
    return habitaciones.value.filter((hab) => !hab.active);
  }

  return habitaciones.value;
});

const roomCounts = computed(() => ({
  all: habitaciones.value.length,
  available: habitaciones.value.filter((hab) => hab.active).length,
  maintenance: habitaciones.value.filter((hab) => !hab.active).length,
}));

const getBrandColor = (token, fallback) =>
  typeof window !== "undefined"
    ? getComputedStyle(document.documentElement).getPropertyValue(token).trim() || fallback
    : fallback;

const COLOR_APPLE = getBrandColor("--k-apple", "#8BCF5B");
const COLOR_FOREST = getBrandColor("--k-forest", "#0f3b2a");
const COLOR_DANGER = getBrandColor("--k-danger", "#e74c3c");

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
    Swal.fire({ icon: "error", title: "Faltan algunos datos", text: "Completa la información principal y la distribución de camas para continuar." });
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
      Swal.fire({
        icon: "success",
        title: "Espacio actualizado",
        text: "La habitación ahora está lista para recibir huéspedes 🌿",
        timer: 1800,
        showConfirmButton: false
      });
    } else {
      await createRoom(roomForm.value, arrayDeArchivos);
      Swal.fire({
        icon: "success",
        title: "Espacio registrado",
        text: "La habitación ahora está lista para recibir huéspedes 🌿",
        timer: 1800,
        showConfirmButton: false
      });
    }

    resetForm();
    await cargarHabitaciones();
    if (closeBtnRef.value) closeBtnRef.value.click();

  } catch (error) {
    console.error("Error al guardar:", error);
    Swal.fire({ icon: "error", title: "No pudimos guardar este espacio", text: "Verifica los datos o tu conexión e inténtalo nuevamente." });
  } finally {
    isSubmitting.value = false;
  }
};

const eliminarHabitacion = async (id) => {
  const result = await Swal.fire({
    title: '¿Deseas retirar esta habitación del inventario?', text: "Podrás registrar un espacio similar nuevamente cuando lo necesites.", icon: 'warning',
    showCancelButton: true, confirmButtonColor: COLOR_APPLE, cancelButtonColor: COLOR_FOREST,
    confirmButtonText: 'Sí, retirarla', cancelButtonText: 'Conservar'
  });

  if (result.isConfirmed) {
    try {
      await deleteRoom(id);
      Swal.fire({ icon: 'success', title: 'Espacio retirado', text: 'La lista quedó actualizada correctamente.', timer: 1600, showConfirmButton: false });
      await cargarHabitaciones(); 
    } catch (error) {
      Swal.fire('No fue posible completar la acción', 'Inténtalo nuevamente en unos segundos.', 'error');
    }
  }
};

const eliminarImagenExistente = async (index, imageUrl) => {
  const result = await Swal.fire({
    title: '¿Borrar esta foto?', text: "Se eliminará permanentemente.", icon: 'warning',
    showCancelButton: true, confirmButtonColor: COLOR_DANGER, cancelButtonColor: COLOR_FOREST,
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
  // 1. Anulamos el evento de error para romper el bucle infinito
  e.target.onerror = null; 
  
  // 2. Intentamos cargar la imagen de reemplazo
  e.target.src = 'https://via.placeholder.com/60x50?text=Sin+Foto';
};

const seleccionarPrincipal = (imgUrl) => {
  roomForm.value.main_image = imgUrl;
};

const abrirCalendario = (habitacion) => {
  if (!habitacion) return;
  habitacionSeleccionada.value = { ...habitacion };
  modalVisible.value = true;
};

const cerrarCalendario = () => {
  modalVisible.value = false;
  habitacionSeleccionada.value = null;
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
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
      <div>
        <p class="brand-handmade mb-1">Espacios listos para recibir viajeros</p>
        <h2 class="section-title mb-1 d-flex align-items-center gap-2">
          <font-awesome-icon icon="fa-solid fa-bed" />
          Gestión de Habitaciones
        </h2>
        <p class="text-muted mb-0">Organiza disponibilidad, mantenimiento y calendario con una vista clara y serena.</p>
      </div>
      
      <button @click="prepararCreacion" class="btn btn-kofan shadow-sm rounded-pill px-4" data-bs-toggle="modal" data-bs-target="#modalHabitacion">
        <font-awesome-icon icon="fa-solid fa-leaf" class="me-2" />
        Nueva Habitación
      </button>
    </div>

    <div class="filter-chip-group mb-4">
      <button class="filter-chip" :class="{ active: roomFilter === 'all' }" @click="roomFilter = 'all'">
        <font-awesome-icon icon="fa-solid fa-bed" class="me-2" />
        Todas
        <span class="chip-count">{{ roomCounts.all }}</span>
      </button>
      <button class="filter-chip" :class="{ active: roomFilter === 'available' }" @click="roomFilter = 'available'">
        <font-awesome-icon icon="fa-solid fa-leaf" class="me-2" />
        Disponibles
        <span class="chip-count">{{ roomCounts.available }}</span>
      </button>
      <button class="filter-chip" :class="{ active: roomFilter === 'maintenance' }" @click="roomFilter = 'maintenance'">
        <font-awesome-icon icon="fa-solid fa-broom" class="me-2" />
        Mantenimiento
        <span class="chip-count">{{ roomCounts.maintenance }}</span>
      </button>
    </div>

    <div class="card eco-card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="table-responsive p-0">
        <table class="table table-hover align-middle mb-0 table-serene">
          <thead class="table-soft">
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
            <tr v-if="isLoading">
              <td colspan="6" class="text-center py-5">
                <div class="spinner-border" style="color: var(--k-apple);" role="status"></div>
                <p class="brand-handmade mt-3 mb-0">Preparando los espacios del hotel...</p>
              </td>
            </tr>

            <tr v-else-if="habitacionesFiltradas.length === 0">
              <td colspan="6" class="text-center text-muted py-5">
                <font-awesome-icon icon="fa-solid fa-leaf" class="display-6 mb-3 d-block" style="color: var(--k-apple);" />
                <p class="empty-state-copy mb-1">Aún no hay habitaciones para este filtro.</p>
                <small>Cuando registres un nuevo espacio, aparecerá aquí.</small>
              </td>
            </tr>
            
            <tr v-for="hab in habitacionesFiltradas" :key="hab.id || hab._id" class="align-middle">
              <td class="ps-4">
                <div class="d-flex align-items-center">
                  <img 
                    :src="`${API_BASE_URL}${hab.main_image}`" 
                    class="rounded me-3 border shadow-sm" 
                    style="width: 60px; height: 50px; object-fit: cover;"
                    @error="manejarErrorImagen"
                  >
                  <div>
                    <div class="fw-bold text-kofan">{{ hab.name }}</div>
                    <small class="text-muted">N° {{ hab.room_number }}</small>
                  </div>
                </div>
              </td>

              <td class="fw-semibold text-kofan">
                ${{ hab.price.toLocaleString('es-CO') }}
              </td>

              <td class="text-muted">
                {{ hab.capacity }} pers.
              </td>

              <td>
                <span :class="hab.active ? 'badge badge-soft-success px-3 py-2 rounded-pill' : 'badge badge-soft-maintenance px-3 py-2 rounded-pill'">
                  <font-awesome-icon :icon="hab.active ? 'fa-solid fa-leaf' : 'fa-solid fa-broom'" class="me-1" />
                  {{ hab.active ? 'Disponible' : 'Mantenimiento' }}
                </span>
              </td>

              <td class="text-center align-middle">
                <button @click="abrirCalendario(hab)" class="btn btn-sm btn-soft-sky rounded-pill px-3 fw-medium shadow-sm" style="font-size: 0.82rem;">
                  <font-awesome-icon icon="fa-solid fa-calendar-days" class="me-1" /> Ver Fechas
                </button>
              </td>

              <td class="text-center align-middle">
                <div class="d-flex justify-content-center gap-2">
                  
                  <button 
                    class="btn btn-sm btn-outline-secondary rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                    style="width: 35px; height: 35px;"
                    data-bs-toggle="modal" 
                    data-bs-target="#modalHabitacion"
                    @click="prepararEdicion(hab)"
                    title="Editar habitación"
                  >
                    <font-awesome-icon :icon="['far', 'pen-to-square']" class="fs-6" />
                  </button>
                  
                  <button 
                    class="btn btn-sm btn-outline-danger rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                    style="width: 35px; height: 35px;"
                    @click="eliminarHabitacion(hab.id || hab._id)"
                    title="Retirar habitación"
                  >
                    <font-awesome-icon icon="fa-solid fa-trash" class="fs-6" />
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
        <div class="modal-content border-0 shadow-lg eco-card">
          <div class="modal-header modal-soft-header border-0">
            <h5 class="modal-title section-title mb-0">
              <font-awesome-icon :icon="isEditing ? 'fa-solid fa-bed' : 'fa-solid fa-leaf'" class="me-2" />
              {{ isEditing ? 'Editar Habitación' : 'Registrar Habitación' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetForm"></button>
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
                    <option value="cabana">Cabaña Independiente</option>
                    <option value="habitacion">Habitación en Maloka</option>
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
                  <p class="text-muted small mb-3">Haz clic en la <font-awesome-icon icon="fa-solid fa-star" class="tone-sand" /> para elegir la foto principal.</p>
                  
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
                          <font-awesome-icon icon="fa-solid fa-trash" class="image-action-icon" />
                        </button>

                        <button 
                          v-if="imgUrl !== roomForm.main_image"
                          type="button" 
                          class="btn btn-light btn-sm position-absolute rounded-circle d-inline-flex align-items-center justify-content-center shadow" 
                          style="width: 28px; height: 28px; bottom: 5px; left: 5px;"
                          @click.stop="seleccionarPrincipal(imgUrl)"
                          title="Hacer foto principal"
                        >
                          <font-awesome-icon icon="fa-solid fa-star" class="image-action-icon tone-sand" />
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
              <button type="submit" class="btn btn-kofan px-4 rounded-pill shadow-sm" :disabled="isSubmitting">
                {{ isSubmitting ? 'Guardando...' : (isEditing ? 'Guardar cambios' : 'Guardar habitación') }}
              </button>
            </div>
          </form>

        </div>
      </div>
    </div>

    <RoomCalendarModal 
      v-if="modalVisible && habitacionSeleccionada"
      :show="modalVisible" 
      :habitacion="habitacionSeleccionada"
      @close="cerrarCalendario"
      @reservaCreada="cargarHabitaciones" 
    />
  </div>
</template>

<style scoped>
.filter-chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.btn-kofan:hover {
  box-shadow: 0 10px 22px rgba(139, 207, 91, 0.18);
}

.filter-chip {
  border: 1px solid var(--k-border);
  background: var(--k-offwhite);
  padding: 0.65rem 1rem;
  border-radius: 999px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.filter-chip:hover {
  background: var(--k-apple-soft);
  border-color: rgba(139, 207, 91, 0.4);
}

.filter-chip.active {
  background: rgba(139, 207, 91, 0.2);
  color: var(--k-forest);
  border-color: rgba(139, 207, 91, 0.45);
  box-shadow: 0 8px 18px rgba(139, 207, 91, 0.14);
}

.chip-count {
  margin-left: 0.45rem;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.8);
  font-size: 0.75rem;
}

.tone-sand {
  color: var(--k-sand);
}

.image-action-icon {
  font-size: 0.8rem;
}

.table-soft th {
  background: rgba(52, 152, 219, 0.08) !important;
}

.table-serene tbody tr:hover {
  background: rgba(52, 152, 219, 0.1);
}

.empty-state-copy {
  font-size: 1.1rem;
}

.badge-soft-success {
  background: rgba(139, 207, 91, 0.18);
  color: var(--k-forest);
  border: 1px solid rgba(139, 207, 91, 0.45);
}

.badge-soft-maintenance {
  background: var(--k-sky-soft);
  color: var(--k-sky);
  border: 1px solid rgba(52, 152, 219, 0.25);
}

.modal-soft-header {
  background: linear-gradient(135deg, var(--k-sky-soft) 0%, var(--k-offwhite) 100%);
}

.border-dashed {
  border-style: dashed !important;
}

.photo-card {
  overflow: hidden;
}

.principal-highlight {
  background-color: rgba(139, 207, 91, 0.12);
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
  width: 28px;
  height: 28px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.2s ease-in-out;
}

.btn-trash { right: 8px; }
.btn-star { right: 42px; }

.photo-card:hover .action-btn {
  opacity: 1;
  transform: scale(1);
}
</style>