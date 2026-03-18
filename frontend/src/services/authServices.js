import apiClient from "@/api/apiClient";

// LOGIN: Autentica y retorna { access_token, refresh_token, token_type }
// El guardado en store/localStorage es responsabilidad exclusiva de auth.js
export const login = async (credentials) => {
  const formData = new URLSearchParams();
  formData.append("username", credentials.username);
  formData.append("password", credentials.password);

  const response = await apiClient.post("/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  return response.data;
};

// REGISTRO: Crea un nuevo usuario → POST /register/
// El backend solo devuelve { message, user_id }, NO devuelve token.
// El login automático posterior es responsabilidad del componente Register.vue.
export const register = async (userData) => {
  const response = await apiClient.post("/register/", userData);
  return response.data;
};

// PERFIL: Obtiene los datos completos del usuario logueado (incluye rol).
// El interceptor de apiClient adjunta el token automáticamente desde localStorage.
export const getUserProfile = async () => {
  const response = await apiClient.get("/users/me");
  return response.data;
};