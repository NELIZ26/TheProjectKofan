<script setup>
import { ref, onMounted } from 'vue';
import { getRoomLogs } from '@/services/roomService';
import RoomHistoryModal from '@/components/RoomHistoryModal.vue';

const logs = ref([]);
const isLoading = ref(true);
const modalVisible = ref(false); 

const fetchLogs = async () => {
  try {
    isLoading.value = true;
    const response = await getRoomLogs(1, 3); 
    logs.value = response.data || []; 
  } catch (error) {
    console.error("Error cargando logs de la tarjeta:", error);
    logs.value = [];
  } finally {
    isLoading.value = false;
  }
};

const formatTime = (dateStr) => {
  if (!dateStr) return '';
  return new Intl.DateTimeFormat('es-CO', { 
    hour: '2-digit', minute: '2-digit' 
  }).format(new Date(dateStr));
};

onMounted(fetchLogs);
</script>

<template>
  <div class="card border-0 shadow-sm rounded-4 p-4">
    
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="fw-bold mb-0">Historial de Habitaciones</h5>
      <span class="text-muted small fw-bold">{{ logs.length }} mov.</span>
    </div>

    <div v-if="isLoading" class="text-center py-4">
      <div class="spinner-border spinner-border-sm text-success"></div>
    </div>

    <div v-else-if="logs.length === 0" class="text-center text-muted py-3 small">
      No hay registros recientes.
    </div>

    <div v-else>
      <div v-for="(log, index) in logs.slice(0, 3)" :key="index" 
           class="d-flex align-items-center bg-white border shadow-sm rounded-3 py-2 px-3 mb-2 notification-item">
        
        <div :class="['activity-dot me-3 flex-shrink-0', log.action === 'ELIMINACIÓN' ? 'bg-danger' : log.action === 'CREACIÓN' ? 'bg-success' : 'bg-primary']"></div>
        
        <div class="flex-grow-1 min-w-0">
          <h6 class="mb-0 fw-bold small text-truncate">{{ log.room_name }}</h6>
          <p class="mb-0 text-muted extra-small text-truncate text-uppercase">
            {{ log.action }} por {{ log.user ? log.user.split('@')[0] : 'Sistema' }}
          </p>
        </div>
        
        <div class="text-muted extra-small fw-bold ms-2 flex-shrink-0">
          {{ formatTime(log.timestamp) }}
        </div>
      </div>
    </div>

    <button 
      @click="modalVisible = true" 
      class="btn btn-light btn-sm w-100 mt-2 fw-bold text-muted border-0 hover-gray"
      :disabled="isLoading"
    >
      Ver historial completo
    </button>

    <RoomHistoryModal :show="modalVisible" @close="modalVisible = false" />
  </div>
</template>

<style scoped>
.activity-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.extra-small { 
  font-size: 0.70rem; 
}

.rounded-4 {
  border-radius: 1.25rem !important;
}

.hover-gray:hover {
  background-color: #e9ecef !important;
}

.min-w-0 {
  min-width: 0;
}

.notification-item {
  transition: all 0.2s ease-in-out;
  border-color: #f0f0f0 !important;
}

.notification-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.08)!important;
}
</style>