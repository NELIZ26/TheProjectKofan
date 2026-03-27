import { defineStore } from "pinia";
import apiClient from "@/api/apiClient"; // Tu cliente de Axios

export const useConfigStore = defineStore("config", {
  state: () => ({
    // Valores por defecto mientras carga
    data: {
      hotel_name: "Kofán Hospedaje",
      logo_url: "",
      contact_email: "",
      phone: "",
      address: "",
      social_facebook: "",
      social_instagram: "",
    },
    isLoaded: false, // Para saber si ya pedimos los datos
  }),
  
  actions: {
    async fetchSiteConfig() {
      // Si ya los cargamos, no volvemos a hacer la petición
      if (this.isLoaded) return; 
      
      try {
        const response = await apiClient.get("/config");
        this.data = response.data;
        this.isLoaded = true;
      } catch (error) {
        console.error("Error al cargar la configuración de Kofán:", error);
      }
    }
  }
});