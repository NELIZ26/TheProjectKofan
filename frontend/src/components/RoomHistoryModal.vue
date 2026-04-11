<script setup>
import { ref, watch } from 'vue';
import { getRoomLogs } from '@/services/roomService';

const props = defineProps({
  show: Boolean
});

const emit = defineEmits(['close']);

const logs = ref([]);
const isLoading = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const totalRecords = ref(0);
const limit = 8; // Registros por página

// Mantiene un registro de qué filas están "expandidas" para ver los detalles
const expandedRows = ref([]);

const fetchLogs = async (page = 1) => {
  isLoading.value = true;
  try {
    const response = await getRoomLogs(page, limit);
    logs.value = response.data;
    totalRecords.value = response.total;
    totalPages.value = Math.ceil(response.total / limit);
    currentPage.value = response.page;
  } catch (error) {
    console.error("Error cargando historial completo:", error);
  } finally {
    isLoading.value = false;
  }
};

const toggleRow = (logId) => {
  const index = expandedRows.value.indexOf(logId);
  if (index === -1) {
    expandedRows.value.push(logId);
  } else {
    expandedRows.value.splice(index, 1);
  }
};

const formatTime = (dateStr) => {
  return new Intl.DateTimeFormat('es-CO', { 
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' 
  }).format(new Date(dateStr));
};

const nextPage = () => { if (currentPage.value < totalPages.value) fetchLogs(currentPage.value + 1); };
const prevPage = () => { if (currentPage.value > 1) fetchLogs(currentPage.value - 1); };

// Escucha cuando el modal se abre para cargar los datos
watch(() => props.show, (newVal) => {
  if (newVal) fetchLogs(1);
});
</script>

<template>
  <div v-if="show" class="modal-backdrop fade show"></div>
  <div class="modal fade show d-block" tabindex="-1" role="dialog" v-if="show" @click.self="$emit('close')">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow-lg rounded-4">
        
        <div class="modal-header bg-dark text-white border-0">
          <h5 class="modal-title fw-bold">
            <i class="bi bi-clock-history me-2"></i> Registro de Auditoría de Habitaciones
          </h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>

        <div class="modal-body p-0 bg-light">
          <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border text-success" role="status"></div>
            <p class="text-muted mt-2 small">Cargando registros...</p>
          </div>

          <div v-else-if="logs.length === 0" class="text-center py-5 text-muted">
            No hay movimientos registrados.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0 bg-white">
              <thead class="table-light text-muted small text-uppercase">
                <tr>
                  <th class="ps-4">Fecha y Hora</th>
                  <th>Habitación</th>
                  <th>Acción</th>
                  <th>Usuario</th>
                  <th class="text-end pe-4">Detalles</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="log in logs" :key="log._id">
                  <tr>
                    <td class="ps-4 small text-muted">{{ formatTime(log.timestamp) }}</td>
                    <td class="fw-bold">{{ log.room_name }}</td>
                    <td>
                      <span :class="{'badge bg-success-subtle text-success': log.action === 'CREACIÓN', 'badge bg-danger-subtle text-danger': log.action === 'ELIMINACIÓN', 'badge bg-primary-subtle text-primary': log.action.includes('ACTUALIZACIÓN')}">
                        {{ log.action }}
                      </span>
                    </td>
                    <td class="small">{{ log.user.split('@')[0] }}</td>
                    <td class="text-end pe-4">
                      <button v-if="log.changes && log.changes.length > 0" 
                              @click="toggleRow(log._id)" 
                              class="btn btn-sm btn-outline-dark rounded-pill" style="font-size: 0.75rem;">
                        {{ expandedRows.includes(log._id) ? 'Ocultar' : 'Ver Cambios' }}
                      </button>
                      <span v-else class="text-muted small" style="font-size: 0.75rem;">Sin info técnica</span>
                    </td>
                  </tr>

                  <tr v-if="expandedRows.includes(log._id)">
                    <td colspan="5" class="bg-light p-0">
                      <div class="p-3 ps-5 border-start border-4 border-primary bg-white m-2 rounded shadow-sm">
                        <h6 class="fw-bold small mb-2 text-muted">Valores Modificados:</h6>
                        <div class="row g-2">
                          <div v-for="(change, idx) in log.changes" :key="idx" class="col-md-4">
                            <div class="p-2 border rounded" style="font-size: 0.8rem;">
                              <div class="fw-bold text-uppercase mb-1">{{ change.field }}</div>
                              <div class="text-danger text-decoration-line-through">De: {{ change.old || 'Vacío' }}</div>
                              <div class="text-success fw-bold">A: {{ change.new }}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>

        <div class="modal-footer bg-white border-top-0 d-flex justify-content-between align-items-center p-3">
          <span class="text-muted small">Total: {{ totalRecords }} registros</span>
          
          <div class="d-flex align-items-center gap-3">
            <button @click="prevPage" :disabled="currentPage === 1" class="btn btn-sm btn-outline-secondary rounded-pill px-3">
              <i class="bi bi-chevron-left"></i> Anterior
            </button>
            <span class="small fw-bold text-dark">Pág. {{ currentPage }} de {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="btn btn-sm btn-outline-secondary rounded-pill px-3">
              Siguiente <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop { background-color: rgba(0, 0, 0, 0.5); }
.modal { display: block; z-index: 1055; }
</style>