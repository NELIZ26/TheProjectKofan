import axios from "axios";
import { useAuthStore } from "@/stores/auth"; 
import router from "@/router"; 

// CAMBIO AQUÍ: Ahora apuntamos al prefijo del proxy definido en vite.config.js
// Esto hará que las peticiones vayan a http://localhost:5173/api/... 
// y Vite las redirija al puerto 8000.
const base = "/api"; 

const apiClient = axios.create({
    baseURL: base,
    headers: {
        'Content-Type': 'application/json',
    },
});

// --- INTERCEPTOR DE PETICIONES (Ida) ---
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    const tokenType = localStorage.getItem('token_type');
    if (token && tokenType) {
        config.headers['Authorization'] = `${tokenType} ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// --- 🚔 INTERCEPTOR DE RESPUESTAS (Vuelta) ---
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            const auth = useAuthStore();
            auth.logout(); 
            router.push({ name: "login" });
        }
        return Promise.reject(error);
    }
);

export default apiClient;