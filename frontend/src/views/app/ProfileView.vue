<script setup>
import { ref, onMounted } from "vue"; // 🟢 Añadimos onMounted
import { useAuthStore } from "@/stores/auth";
import apiClient from "@/api/apiClient"; // 🟢 Importamos el cliente para hacer la petición

const auth = useAuthStore();

// 🟢 Estado de solo lectura
const formData = ref({
  full_name: auth.user?.full_name || "",
  phone: auth.user?.phone || "",
  role: auth.user?.role || "Cliente",
  email: auth.user?.email || "cliente@kofan.com",
  number_document: auth.user?.number_document || "12223333"
});

// 🟢 Array vacío que se llenará con la base de datos
const avisosRecientes = ref([]);

// 🟢 Función para traer los datos reales
const cargarAvisosRecientes = async () => {
  try {
    const response = await apiClient.get('/api/notificaciones/mis-avisos');
    
    // La magia está aquí: .slice(0, 2) corta la lista y solo nos deja los 2 avisos más nuevos
    avisosRecientes.value = response.data.slice(0, 2);
    
  } catch (error) {
    console.error("Error cargando alertas recientes:", error);
  }
};

// 🟢 Ejecutar al cargar la pantalla
onMounted(() => {
  cargarAvisosRecientes();
});
</script>

<template>
  <div class="perfil-section">
    <div class="mb-4">
      <h3 class="fw-bold text-dark mb-1">Mi Panel</h3>
      <p class="text-muted small mb-0">Resumen de tu cuenta y alertas recientes</p>
    </div>

    <div class="card border-0 shadow-sm rounded-4 mb-4 overflow-hidden position-relative tarjeta-kofan-suave">
      
      <div class="card-body p-4 p-md-5 position-relative z-1">
        <span class="badge bg-white text-success rounded-pill mb-3 px-3 py-2 shadow-sm border border-success-subtle">
          <i class="bi bi-star-fill text-warning me-1"></i> {{ formData.role === 'admin' ? 'Administrador' : 'Cliente Kofán' }}
        </span>
        <h3 class="fw-bold mb-2 verde-kofan">{{ formData.full_name || 'Usuario Kofán' }}</h3>
        
        <div class="d-flex flex-wrap gap-4 mt-3 verde-kofan opacity-75 fw-medium">
          <span><i class="bi bi-envelope-fill me-2"></i> {{ formData.email }}</span>
          <span><i class="bi bi-person-vcard-fill me-2"></i> {{ formData.number_document }}</span>
          <span v-if="formData.phone"><i class="bi bi-telephone-fill me-2"></i> {{ formData.phone }}</span>
        </div>
      </div>
    </div>

    <div class="mt-5">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="fw-bold text-dark"><i class="bi bi-bell-fill text-muted me-2"></i> Avisos Recientes</h5>
        <router-link :to="{ name: 'account-notifications' }" class="btn btn-sm btn-link text-decoration-none text-success fw-bold">
          Ver todos
        </router-link>
      </div>

      <div class="d-flex flex-column gap-3">
        <div v-if="avisosRecientes.length === 0" class="text-center py-4 bg-white rounded-4 shadow-sm border">
          <i class="bi bi-bell-slash text-muted fs-1 mb-2 d-block"></i>
          <p class="text-muted small mb-0">No tienes alertas nuevas.</p>
        </div>

        <div v-for="aviso in avisosRecientes" :key="aviso.id" class="card border-0 shadow-sm rounded-4 aviso-card" :class="`border-start border-4 border-${aviso.colorTheme}`">
          <div class="card-body p-3 d-flex align-items-center gap-3">
            <div class="rounded-3 d-flex align-items-center justify-content-center flex-shrink-0" :class="`bg-${aviso.colorTheme} bg-opacity-10 text-${aviso.colorTheme}`" style="width: 45px; height: 45px;">
              <i :class="aviso.icono" class="fs-5"></i>
            </div>
            <div class="flex-grow-1">
              <div class="d-flex justify-content-between align-items-center">
                <h6 class="fw-bold mb-0 text-dark">{{ aviso.titulo }}</h6>
                <small class="text-muted">{{ aviso.fecha }}</small>
              </div>
              <p class="mb-0 text-secondary small">{{ aviso.mensaje }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.verde-kofan { color: #0f3b2a !important; }

/* 🟢 Estilo exacto para el fondo verde suave */
.tarjeta-kofan-suave {
  background-color: #eafaf1; /* Verde menta muy suave */
  border: 1px solid #d4ebd9 !important; /* Borde un poco más oscuro para darle profundidad */
}

.aviso-card { transition: transform 0.2s ease; background-color: white; }
.aviso-card:hover { transform: translateX(4px); }
</style>