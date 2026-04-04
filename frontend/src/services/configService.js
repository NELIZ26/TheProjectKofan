import apiClient from '@/api/apiClient';

export const fetchConfig = async () => {
  try {
    const { data } = await apiClient.get('/config');
    return data;
  } catch (error) {
    console.error("Error al obtener la configuración:", error);
    throw error;
  }
};

export const saveConfig = async (configData) => {
  try {
    const { data } = await apiClient.put('/config', configData);
    return data;
  } catch (error) {
    console.error("Error al guardar la configuración:", error);
    throw error;
  }
};

export const uploadLogo = async (formData) => {
  try {
    const { data } = await apiClient.post('/config/logo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  } catch (error) {
    console.error("Error al subir el logo:", error);
    throw error;
  }
};