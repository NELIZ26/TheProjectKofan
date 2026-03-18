import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
 
export const useAuthStore = defineStore('auth', () => {
  // Estado inicial: recupera datos del localStorage para sobrevivir recargas de página
  const user = ref(JSON.parse(localStorage.getItem('userData')) || null);
  const token = ref(localStorage.getItem('token') || null);
  const tokenType = ref(localStorage.getItem('token_type') || 'Bearer');
 
  // Getters
  const isLogged = computed(() => !!token.value);
 
  // Normalizado a minúsculas para evitar problemas de comparación ("Admin" vs "admin")
  const userRole = computed(() => user.value?.role?.toLowerCase() || null);
  const isAdmin = computed(() => userRole.value === 'admin');
 
  // Acción de login:
  // Primero guarda el token en localStorage para que el interceptor de apiClient
  // pueda adjuntarlo en la llamada siguiente a /users/me (getUserProfile).
  const login = (userData, access_token, type = 'Bearer') => {
    // 1. Persistir token primero (el interceptor lo necesita para /users/me)
    localStorage.setItem('token', access_token);
    localStorage.setItem('token_type', type);
    localStorage.setItem('userData', JSON.stringify(userData));
 
    // 2. Actualizar el estado reactivo
    user.value = userData;
    token.value = access_token;
    tokenType.value = type;
  };
 
  const logout = () => {
    user.value = null;
    token.value = null;
    tokenType.value = 'Bearer';
 
    // Limpieza total del localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('userData');
  };
 
  return { user, token, tokenType, isLogged, userRole, isAdmin, login, logout };
});