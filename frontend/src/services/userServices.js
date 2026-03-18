import apiClient from "@/api/apiClient";

// Obtener todos los usuarios con paginación
export const getAllUsers = async (page = 1, limit = 10) => {
  const response = await apiClient.get("/users", {
    params: { page, limit },
  });
  return response.data;
};

// Obtener un usuario por ID
export const getUserById = async (id) => {
  const response = await apiClient.get(`/users/${id}`);
  return response.data;
};

// Crear un nuevo usuario (desde el panel admin)
export const createUser = async (userData) => {
  const response = await apiClient.post("/users", userData);
  return response.data;
};

// Actualizar datos de un usuario
export const updateUser = async (id, userData) => {
  const response = await apiClient.put(`/users/${id}`, userData);
  return response.data;
};

// Cambiar estado activo/inactivo de un usuario
export const toggleUserStatus = async (id) => {
  const response = await apiClient.patch(`/users/${id}/toggle-status`);
  return response.data;
};

// Eliminar un usuario
export const deleteUser = async (id) => {
  const response = await apiClient.delete(`/users/${id}`);
  return response.data;
};