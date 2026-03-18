<template>
  <div>
    <div class="input-group">
      <input
        :type="inputType"
        class="form-control"
        :class="{ 'is-invalid': error }"
        :placeholder="placeholder"
        v-model="model"
      />

      <button
        class="btn btn-outline-secondary"
        type="button"
        @click="toggle"
      >
        <i :class="icon"></i>
      </button>
    </div>

    <!-- fuera del input-group -->
    <div v-if="error" class="invalid-feedback d-block">
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
const icon = computed(() => visible.value ? 'bi bi-eye-slash' : 'bi bi-eye')

const toggle = () => {
  visible.value = !visible.value
}

const model = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})
</script>