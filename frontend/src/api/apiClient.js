import axios from "axios";

const base = import.meta.env.VITE_BACKEND_URL;

const apiClient = axios.create({
    baseURL: base,
    headers: {
        'Content-Type': 'application/json',
    },})
//Agregar un interceptor para agregar el token de autenticacion a cada solicitud
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

export default apiClient;