import axios from "axios";
import { useAuthStore } from "@/stores/auth"; // 🟢 1. Importamos el store
import router from "@/router"; // 🟢 2. Importamos el router

const base = import.meta.env.VITE_BACKEND_URL;

const apiClient = axios.create({
    baseURL: base,
    headers: {
        'Content-Type': 'application/json',
    },
});

// --- INTERCEPTOR DE PETICIONES (Ida) ---
// Agregar un interceptor para agregar el token de autenticación a cada solicitud
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
// Revisa si el backend nos rechaza por token vencido
apiClient.interceptors.response.use(
    (response) => {
        // Todo salió bien (200 OK), dejamos pasar la respuesta
        return response;
    },
    (error) => {
        // Si el backend nos responde con un 401 (No autorizado / Token vencido)
        if (error.response && error.response.status === 401) {
            const auth = useAuthStore();
            
            // 1. Ejecutamos la limpieza en Pinia (esto debe borrar el localStorage también)
            auth.logout(); 
            
            // 2. Pateamos al usuario a la vista de login a la fuerza
            router.push({ name: "login" });
        }
        
        // Devolvemos el error por si la vista necesita mostrar una alerta
        return Promise.reject(error);
    }
);

export default apiClient;