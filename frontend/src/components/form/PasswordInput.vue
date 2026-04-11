<template>
  <div>
    <div class="input-group">
      <input
        :type="inputType"
        class="form-control custom-input border-end-0 shadow-none"
        :class="{ 'is-invalid': error }"
        :placeholder="placeholder"
        v-model="model"
      />

      <span
        class="input-group-text bg-white border-start-0 custom-icon-container"
        :class="{ 'border-danger': error }"
        @click="toggle"
        title="Mostrar/Ocultar contraseña"
      >
        <font-awesome-icon :icon="icon" class="text-muted" />
      </span>
    </div>

    <div v-if="error" class="invalid-feedback d-block text-start">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)

const inputType = computed(() => visible.value ? 'text' : 'password')

/* UX correcta */
const icon = computed(() => visible.value ? ['fas', 'eye-slash'] : ['fas', 'eye'])

const toggle = () => {
  visible.value = !visible.value
}

const model = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})
</script>

<style scoped>
/* Estilo para que el ojito tenga el puntero de clic y coincida con el borde de tu custom-input */
.custom-icon-container {
  cursor: pointer;
  border-color: #dee2e6; /* Ajusta este color si el borde de tus otros inputs es diferente */
  border-top-right-radius: 8px; /* Redondeo derecho */
  border-bottom-right-radius: 8px; /* Redondeo derecho */
}

/* Si el input está en error (is-invalid), aseguramos que el borde del ojito también se ponga rojo */
.border-danger {
  border-color: #dc3545 !important;
}
</style>