<script setup>
import { ref, onMounted } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";
import ModalUsuario from "@/components/ModalUsuario.vue";

const usuarios = ref([]);
const cargando = ref(false);
const cargandoRegistro = ref(false);
const mostrarModal = ref(false);
const usuarioSeleccionado = ref(null); // 🟢 Aquí guardamos el usuario a editar

const cargarUsuarios = async () => {
  try {
    cargando.value = true;
    const { data } = await apiClient.get("/users/");
    usuarios.value = data;
  } catch (error) {
    Swal.fire("Error", "No se pudo obtener la lista", "error");
  } finally {
    cargando.value = false;
  }
};

// 🟢 Función para abrir modal en modo "Crear"
const abrirNuevo = () => {
  usuarioSeleccionado.value = null;
  mostrarModal.value = true;
};

// 🟢 Función para abrir modal en modo "Editar"
const abrirEdicion = (user) => {
  usuarioSeleccionado.value = { ...user };
  mostrarModal.value = true;
};

// 🟢 Función unificada para Guardar o Actualizar
const guardarUsuario = async (datos) => {
  try {
    cargandoRegistro.value = true;
    
    if (datos.id) {
      // Si tiene ID, es una actualización (PATCH)
      await apiClient.patch(`/users/${datos.id}`, datos);
      Swal.fire("¡Actualizado!", "Los datos del usuario han sido modificados.", "success");
    } else {
      // Si no tiene ID, es uno nuevo (POST)
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

// 🟢 Función para Suspender / Eliminar
// 🟢 Función inteligente para Suspender o Reactivar
const toggleEstado = async (user) => {
  // Asumimos que si is_active no existe, el usuario está activo por defecto
  const estaActivo = user.is_active !== false; 
  const accion = estaActivo ? "Suspender" : "Reactivar";
  const colorBoton = estaActivo ? "#d33" : "#0f3b2a"; // Rojo para suspender, Verde para reactivar

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
      // Llamamos a la ruta DELETE que acabamos de crear en FastAPI
      await apiClient.patch(`/users/${clients.id}/toggle-status`);
      
      Swal.fire(
        "¡Listo!", 
        `El usuario ha sido ${estaActivo ? 'suspendido' : 'reactivado'}.`, 
        "success"
      );
      cargarUsuarios(); // Recargamos la tabla
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
        <font-awesome-icon icon="fa-solid fa-user-plus" class="me-2" />
        Nuevo Usuario
      </button>
    </div>

    <div class="card border-0 shadow-sm rounded-4">
      <div class="table-responsive p-3">
        <table class="table table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th class="ps-3">Nombre</th>
              <th>Documento</th>
              <th>Correo Electrónico</th>
              <th>Rol</th>
              <th>Estado</th> <th class="text-end pe-3">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargando">
              <td colspan="6" class="text-center py-5">
                <div class="spinner-border text-success" role="status"></div>
                <p class="mt-2 text-muted">Consultando base de datos de Kofán...</p>
              </td>
            </tr>

            <tr v-else-if="usuarios.length === 0">
               <td colspan="6" class="text-center py-5 text-muted">No se encontraron usuarios registrados.</td>
            </tr>

            <template v-else>
              <tr v-for="user in usuarios" :key="user.id" :class="{'opacity-50': user.is_active === false}">
                
                <td class="ps-3 fw-bold">{{ user.full_name }}</td>
                
                <td>
                  <span class="text-muted small">{{ user.type_document }}</span><br>
                  {{ user.number_document }}
                </td>
                
                <td>{{ user.email }}</td>
                
                <td>
                  <span 
                    class="badge rounded-pill px-3 py-2" 
                    :class="user.role === 'admin' ? 'bg-dark text-white' : 'bg-light text-dark border'"
                  >
                    <font-awesome-icon 
                      :icon="user.role === 'admin' ? 'fa-solid fa-user-shield' : 'fa-solid fa-user'" 
                      class="me-1 text-success" 
                    />
                    {{ user.role === 'admin' ? 'Administrador' : 'Cliente' }}
                  </span>
                </td>

                <td>
                  <span 
                    class="badge rounded-pill px-3 py-1" 
                    :class="user.is_active !== false ? 'bg-success bg-opacity-10 text-success border border-success' : 'bg-danger bg-opacity-10 text-danger border border-danger'"
                  >
                    <font-awesome-icon :icon="user.is_active !== false ? 'fa-solid fa-circle-check' : 'fa-solid fa-xmark'" class="me-1" />
                    {{ user.is_active !== false ? 'Activo' : 'Suspendido' }}
                  </span>
                </td>

                <td class="text-end pe-3">
                  <button @click="abrirEdicion(user)" class="btn btn-sm btn-outline-primary rounded-circle me-2" title="Editar">
                    <font-awesome-icon icon="fa-solid fa-pen-to-square" />
                  </button>
                  
                  <button 
                    @click="toggleEstado(user)" 
                    class="btn btn-sm rounded-circle" 
                    :class="user.is_active !== false ? 'btn-outline-danger' : 'btn-outline-success'"
                    :title="user.is_active !== false ? 'Suspender' : 'Reactivar'"
                  >
                    <font-awesome-icon :icon="user.is_active !== false ? 'fa-solid fa-lock' : 'fa-solid fa-rotate'" />
                  </button>
                </td>

              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <ModalUsuario 
      :show="mostrarModal" 
      :cargando="cargandoRegistro"
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