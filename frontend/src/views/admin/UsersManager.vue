<script setup>
import { ref, onMounted, defineAsyncComponent } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";

// 🟢 Lazy Loading del Modal (Estándar de calidad Kofán)
import ModalUsuario from "@/components/ModalUsuario.vue";

// 🟢 Constantes para evitar "cadenas mágicas"
const USER_ROLES = {
  ADMIN: "admin",
  CLIENT: "client",
  RECEPCIONISTA: "recepcionista"
};

const usuarios = ref([]);
const cargando = ref(false);
const cargandoRegistro = ref(false);
const mostrarModal = ref(false);
const usuarioSeleccionado = ref(null);

// 🟢 Variables para Paginación del lado del servidor
const paginaActual = ref(1);
const limite = ref(10);
const hayMasRegistros = ref(true);

const cargarUsuarios = async () => {
  try {
    cargando.value = true;
    const skip = (paginaActual.value - 1) * limite.value;
    
    // Conectado con la nueva paginación del backend
    const { data } = await apiClient.get(`/users/?skip=${skip}&limit=${limite.value}`);
    
    usuarios.value = data;
    hayMasRegistros.value = data.length === limite.value; 
  } catch (error) {
    Swal.fire("Error", "No se pudo obtener la lista de usuarios", "error");
  } finally {
    cargando.value = false;
  }
};

const cambiarPagina = (delta) => {
  paginaActual.value += delta;
  cargarUsuarios();
};

const abrirNuevo = () => {
  usuarioSeleccionado.value = null;
  mostrarModal.value = true;
};

const abrirEdicion = (user) => {
  usuarioSeleccionado.value = { ...user };
  mostrarModal.value = true;
};

const guardarUsuario = async (datos) => {
  try {
    cargandoRegistro.value = true;
    
    if (datos.id) {
      await apiClient.patch(`/users/${datos.id}`, datos);
      Swal.fire("¡Actualizado!", "Los datos del usuario han sido modificados.", "success");
    } else {
      await apiClient.post("/users/", datos);
      Swal.fire("¡Creado!", "El usuario ha sido registrado.", "success");
    }

    mostrarModal.value = false;
    cargarUsuarios(); 
  } catch (error) {
    const errorMsg = error.response?.data?.detail || "Hubo un problema procesando la solicitud";
    Swal.fire("Error", errorMsg, "error");
  } finally {
    cargandoRegistro.value = false;
  }
};

const toggleEstado = async (user) => {
  const estaActivo = user.is_active !== false; 
  const accion = estaActivo ? "Suspender" : "Reactivar";
  const colorBoton = estaActivo ? "#d33" : "#0f3b2a"; 

  const result = await Swal.fire({
    title: `¿${accion} usuario?`,
    text: estaActivo 
      ? "El usuario ya no podrá iniciar sesión ni hacer reservas." 
      : "El usuario recuperará su acceso al sistema del hotel.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: colorBoton,
    cancelButtonColor: "#6c757d",
    confirmButtonText: `Sí, ${accion.toLowerCase()}`,
    cancelButtonText: "Cancelar"
  });

  if (result.isConfirmed) {
    try {
      // 🟢 CORREGIDO: clients.id -> user.id
      await apiClient.patch(`/users/${user.id}/toggle-status`);
      
      Swal.fire("¡Listo!", `El usuario ha sido ${estaActivo ? 'suspendido' : 'reactivado'}.`, "success");
      cargarUsuarios(); 
    } catch (error) {
      Swal.fire("Error", "No se pudo cambiar el estado del usuario.", "error");
    }
  }
};

onMounted(() => { cargarUsuarios(); });
</script>

<template>
  <div class="users-manager p-1">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="fw-bold mb-1 text-dark">Gestión de Usuarios</h4>
        <p class="text-muted small">Administra los accesos de clientes y personal del hotel.</p>
      </div>
      <button class="btn btn-dark shadow-sm rounded-pill px-4" @click="abrirNuevo">
        <i class="bi bi-person-plus-fill me-2"></i>
        Nuevo Usuario
      </button>
    </div>

    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th class="ps-4 py-3 text-muted small fw-bold">NOMBRE</th>
              <th class="py-3 text-muted small fw-bold">DOCUMENTO</th>
              <th class="py-3 text-muted small fw-bold">CORREO ELECTRÓNICO</th>
              <th class="py-3 text-muted small fw-bold">ROL</th>
              <th class="py-3 text-muted small fw-bold">ESTADO</th> 
              <th class="text-center py-3 text-muted small fw-bold">ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargando">
              <td colspan="6" class="text-center py-5">
                <div class="spinner-border text-success" role="status"></div>
                <p class="mt-2 text-muted fw-bold">Consultando base de datos de Kofán...</p>
              </td>
            </tr>

            <tr v-else-if="usuarios.length === 0">
               <td colspan="6" class="text-center py-5 text-muted">
                 <i class="bi bi-person-x display-4 mb-3 d-block text-light"></i>
                 No se encontraron usuarios registrados.
               </td>
            </tr>

            <template v-else>
              <tr v-for="user in usuarios" :key="user.id" :class="{'opacity-50 bg-light': user.is_active === false}">
                
                <td class="ps-4 fw-bold text-dark">{{ user.full_name }}</td>
                
                <td>
                  <span class="text-muted small d-block mb-1">{{ user.type_document }}</span>
                  <span class="text-dark">{{ user.number_document }}</span>
                </td>
                
                <td class="text-muted">{{ user.email }}</td>
                
                <td>
                  <span 
                    class="badge rounded-pill px-3 py-2 border" 
                    :class="user.role === USER_ROLES.ADMIN ? 'bg-dark text-white border-dark' : 'bg-light text-secondary'"
                  >
                    <i 
                      :class="user.role === USER_ROLES.ADMIN ? 'bi bi-shield-lock-fill text-success' : 'bi bi-person-fill text-secondary'" 
                      class="me-1" 
                    ></i>
                    {{ user.role === USER_ROLES.ADMIN ? 'Administrador' : 'Cliente' }}
                  </span>
                </td>

                <td>
                  <span 
                    class="badge rounded-pill px-3 py-2" 
                    :class="user.is_active !== false ? 'bg-success bg-opacity-10 text-success border border-success' : 'bg-danger bg-opacity-10 text-danger border border-danger'"
                  >
                    <i :class="user.is_active !== false ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill'" class="me-1"></i>
                    {{ user.is_active !== false ? 'Activo' : 'Suspendido' }}
                  </span>
                </td>

                <td class="text-center align-middle">
                  <div class="d-flex justify-content-center gap-2">
                    <button 
                      @click="abrirEdicion(user)" 
                      class="btn btn-sm btn-outline-dark rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                      style="width: 35px; height: 35px;"
                      title="Editar"
                    >
                      <i class="bi bi-pencil-square fs-6"></i>
                    </button>
                    
                    <button 
                      @click="toggleEstado(user)" 
                      class="btn btn-sm rounded-circle d-inline-flex align-items-center justify-content-center shadow-sm" 
                      style="width: 35px; height: 35px;"
                      :class="user.is_active !== false ? 'btn-outline-danger' : 'btn-outline-success'"
                      :title="user.is_active !== false ? 'Suspender' : 'Reactivar'"
                    >
                      <i :class="user.is_active !== false ? 'bi bi-lock-fill fs-6' : 'bi bi-arrow-repeat fs-6'"></i>
                    </button>
                  </div>
                </td>

              </tr>
            </template>
          </tbody>
        </table>
      </div>
      
      <div class="card-footer bg-light border-top border-0 d-flex flex-column flex-md-row justify-content-between align-items-center p-3">
        <span class="text-muted small fw-bold mb-2 mb-md-0">Página {{ paginaActual }}</span>
        <div class="btn-group shadow-sm">
          <button 
            class="btn btn-sm btn-white border bg-white" 
            :disabled="paginaActual === 1 || cargando" 
            @click="cambiarPagina(-1)"
          >
            <i class="bi bi-chevron-left me-1"></i> Anterior
          </button>
          <button 
            class="btn btn-sm btn-white border bg-white" 
            :disabled="!hayMasRegistros || cargando" 
            @click="cambiarPagina(1)"
          >
            Siguiente <i class="bi bi-chevron-right ms-1"></i>
          </button>
        </div>
      </div>
    </div>
    
    <ModalUsuario 
      v-if="mostrarModal" 
      :show="true" 
      :usuarioEditando="usuarioSeleccionado" 
      @cerrar="mostrarModal = false" 
      @guardar="guardarUsuario" 
    />
  </div>
</template>

<style scoped>
.card {
  border-radius: 15px;
}
.table thead th {
  font-size: 0.75rem;
  text-transform: uppercase;
  font-weight: 700;
  color: #888;
}
.badge {
  font-weight: 500;
  font-size: 0.8rem;
}
</style>