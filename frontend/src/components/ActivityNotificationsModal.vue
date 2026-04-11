<script setup>
import { ref, watch } from 'vue';
import apiClient from '@/api/apiClient';

const props = defineProps({
  show: Boolean
});

const emit = defineEmits(['close']);

const logs = ref([]);
const isLoading = ref(false);

const fetchNotifications = async () => {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/api/notificaciones/mis-avisos');
    
    // 🟢 ESTE CONSOLE.LOG ES LA CLAVE PARA SABER QUÉ LLEGA
    console.log("Respuesta del backend (Avisos):", response.data); 
    
    logs.value = response.data || [];
  } catch (error) {
    console.error("Error cargando mis avisos:", error);
    logs.value = [];
  } finally {
    isLoading.value = false;
  }
};

const marcarTodasComoLeidas = async () => {
  try {
    await apiClient.patch('/api/notificaciones/read-all');
    // Actualizamos la vista para que ya no salgan resaltadas
    logs.value.forEach(log => log.leida = true);
  } catch (error) {
    console.error("Error al marcar como leídas:", error);
  }
};

// Escucha cuando el modal se abre para cargar los datos
watch(() => props.show, (newVal) => {
  if (newVal) {
    fetchNotifications();
  }
});
</script>

<template>
  <div v-if="show" class="modal-backdrop fade show"></div>
  <div class="modal fade show d-block" tabindex="-1" role="dialog" v-if="show" @click.self="$emit('close')">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow-lg rounded-4">
        
        <div class="modal-header text-white border-0">
          <h5 class="modal-title fw-bold">
            <font-awesome-icon :icon="['fas', 'bell']" class="me-2 text-warning" /> Historial de Actividad y Avisos
          </h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>

        <div class="modal-body p-0 bg-light">
          <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="text-muted mt-2 small">Cargando tus notificaciones...</p>
          </div>

          <div v-else-if="logs.length === 0" class="text-center py-5 text-muted">
            <i class="bi bi-inbox display-4 d-block mb-3 text-light"></i>
            No tienes avisos recientes.
          </div>

          <div v-else class="list-group list-group-flush">
            <div v-for="log in logs" :key="log.id" 
                 class="list-group-item list-group-item-action p-3 border-bottom"
                 :class="{'bg-white': log.leida, 'bg-primary-subtle': !log.leida}">
              <div class="d-flex align-items-start gap-3">
                
                <div class="icon-circle shadow-sm flex-shrink-0" :class="`bg-${log.colorTheme}`">
                  <i class="bi text-white" :class="log.icono"></i>
                </div>

                <div class="flex-grow-1 min-w-0">
                  <div class="d-flex justify-content-between align-items-center mb-1">
                    <h6 class="mb-0 fw-bold text-truncate pe-3" :class="{'text-dark': log.leida, 'text-primary': !log.leida}">
                      {{ log.titulo }}
                    </h6>
                    <small class="text-muted text-nowrap" style="font-size: 0.75rem;">{{ log.fecha }}</small>
                  </div>
                  <p class="mb-0 text-muted small" style="white-space: pre-line;">{{ log.mensaje }}</p>
                </div>

              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer bg-white border-top-0 d-flex justify-content-between align-items-center p-3">
          <span class="text-muted small">Últimos {{ logs.length }} avisos registrados</span>
          
          <div class="d-flex gap-2">
            <button @click="marcarTodasComoLeidas" class="btn btn-sm btn-outline-secondary rounded-pill px-3">
              <i class="bi bi-check2-all me-1"></i> Marcar todas leídas
            </button>
            <button @click="$emit('close')" class="btn btn-sm btn-dark rounded-pill px-4 shadow-sm">
              Cerrar
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-header {
  background-color: var(--k-forest-soft);
}
.modal-backdrop { background-color: var(--k-forest); }
.modal { display: block; z-index: 1055; }

.icon-circle {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>