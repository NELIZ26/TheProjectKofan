import apiClient from "@/api/apiClient"; // Usamos tu cliente configurado

// CONFIGURACIÓN: Obtiene los datos del hotel
export const fetchConfig = async () => {
  // Ajusta la ruta '/config' según cómo la vayas a llamar en tu FastAPI
  const response = await apiClient.get("/config/"); 
  return response.data;
};

// CONFIGURACIÓN: Guarda o actualiza los datos del hotel
export const saveConfig = async (configData) => {
  const response = await apiClient.put("/config/", configData);
  return response.data;
};

// CONFIGURACIÓN: Sube el logo del hotel
export const uploadLogo = async (formData) => {
  const response = await apiClient.post("/config/logo", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};