import { defineStore } from "pinia";
import apiClient from "@/api/apiClient";

export const useGalleryStore = defineStore("gallery", {
  state: () => ({
    images: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    // 1. Obtener todas las imágenes
    async fetchImages() {
      this.isLoading = true;
      try {
        const response = await apiClient.get("/gallery/");
        this.images = response.data;
      } catch (error) {
        this.error = "Error al cargar la galería.";
        console.error(error);
      } finally {
        this.isLoading = false;
      }
    },

    // 2. Subir nueva imagen
    async uploadImage(file) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await apiClient.post("/gallery/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        // Agregamos la nueva imagen al principio de la lista
        this.images.unshift(response.data); 
        return { success: true };
      } catch (error) {
        console.error("Error al subir:", error);
        return { success: false, error: error.response?.data?.detail || "Error al subir" };
      }
    },

    // 3. Eliminar imagen
    async deleteImage(imageId) {
      try {
        await apiClient.delete(`/gallery/${imageId}`);
        // Filtramos la imagen eliminada para que desaparezca de la pantalla al instante
        this.images = this.images.filter((img) => img.id !== imageId);
        return { success: true };
      } catch (error) {
        console.error("Error al eliminar:", error);
        return { success: false };
      }
    },
  },
});