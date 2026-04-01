<script setup>
import FormularioRegistro from '@/components/FormularioRegistro.vue';

const props = defineProps({
  show: Boolean,
  cargando: Boolean,
  usuarioEditando: Object // 🟢 Recibimos el usuario a editar
});

const emit = defineEmits(["cerrar", "guardar"]);

const propagarGuardado = (datosDelFormulario) => {
  emit("guardar", datosDelFormulario);
};
</script>

<template>
  <div v-if="show" class="modal fade show d-block bg-dark bg-opacity-50" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content border-0 shadow-lg rounded-4 p-3">
        
        <div class="modal-header border-0 pb-0 position-relative">
          <div class="w-100 text-center">
            <h2 class="fw-bold verde-kofan mb-1">
              {{ usuarioEditando ? 'Editar Usuario' : 'Registrar Nuevo Usuario' }}
            </h2>
            <div class="divider mx-auto mt-2"></div>
          </div>
          <button type="button" class="btn-close position-absolute top-0 end-0 m-3" @click="$emit('cerrar')"></button>
        </div>

        <div class="modal-body p-4">
          <FormularioRegistro 
            :mostrarRol="true" 
            :cargando="props.cargando"
            :usuarioEditando="props.usuarioEditando" 
            @enviar="propagarGuardado" 
          />
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.verde-kofan { color: #0f3b2a; }
.divider { width: 50px; height: 3px; background-color: #0f3b2a; border-radius: 2px; }
.modal { z-index: 1055; }
</style>