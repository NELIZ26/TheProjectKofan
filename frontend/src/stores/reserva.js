import { defineStore } from "pinia";
import { ref, reactive } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";

export const useReservaStore = defineStore("reserva", () => {
  const isModalOpen = ref(false);
  const isSubmitting = ref(false);
  const habitacionSeleccionada = ref(null);

  const selectedDateRange = ref(null); 
  const disabledDates = ref([]); 
  const minDate = ref(new Date().toISOString().split("T")[0]); 

  // 🟢 FORMULARIO ULTRA MINIMALISTA (Solo 3 campos)
  const form = reactive({
    nombreCompleto: "",
    correo: "",
    telefono: "",
  });

  const errors = reactive({
    nombreCompleto: false,
    correo: false,
    telefono: false,
    dates: false, 
  });

  const openModal = async (habitacion = null) => {
    isModalOpen.value = true;
    clearErrors();
    selectedDateRange.value = null; 
    
    if (habitacion) {
      habitacionSeleccionada.value = habitacion;
      await fetchDisabledDates(habitacion.id || habitacion._id);
    }
  };

  const fetchDisabledDates = async (roomId) => {
    try {
      disabledDates.value = []; 
      const response = await apiClient.get(`/rooms/${roomId}/booked-dates`);
      disabledDates.value = response.data.map(reserva => ({
        start: new Date(reserva.fecha_entrada),
        end: new Date(reserva.fecha_salida)
      }));
    } catch (error) {
      console.error("Error cargando fechas ocupadas:", error);
    }
  };

  const closeModal = () => {
    isModalOpen.value = false;
  };

  const clearErrors = () => {
    Object.keys(errors).forEach((key) => (errors[key] = false));
  };

  const resetForm = () => {
    form.nombreCompleto = "";
    form.correo = "";
    form.telefono = "";
    selectedDateRange.value = null; 
    habitacionSeleccionada.value = null;
    clearErrors();
  };

  const validateForm = () => {
    let isValid = true;
    clearErrors();

    if (!selectedDateRange.value?.start || !selectedDateRange.value?.end) { 
      errors.dates = true; isValid = false; 
    }
    if (!form.nombreCompleto.trim()) { errors.nombreCompleto = true; isValid = false; }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!form.correo || !emailRegex.test(form.correo)) { errors.correo = true; isValid = false; }
    if (!form.telefono) { errors.telefono = true; isValid = false; }
    
    return isValid;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      Swal.fire({
        icon: "error",
        title: "Faltan datos",
        text: "Por favor, selecciona las fechas en el calendario y llena tus datos de contacto.",
        confirmButtonColor: "#0f3b2a",
      });
      return false; 
    }

    isSubmitting.value = true;

    // Calcular días y monto
    const checkIn = selectedDateRange.value.start;
    const checkOut = selectedDateRange.value.end;
    const diasEstadia = Math.ceil((checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60 * 24)) || 1;
    const montoCalculado = habitacionSeleccionada.value.price * diasEstadia;
    
    const fechaInString = checkIn.toISOString().split("T")[0];
    const fechaOutString = checkOut.toISOString().split("T")[0];

    Swal.fire({
      title: "Procesando Reserva...",
      allowOutsideClick: false,
      didOpen: () => { Swal.showLoading(); },
    });

    try {
      const payload = {
        habitacion_id: habitacionSeleccionada.value.id || habitacionSeleccionada.value._id, 
        fecha_entrada: fechaInString, 
        fecha_salida: fechaOutString,
        monto_total: montoCalculado,
        acompanantes: [], 
        observaciones: "Reserva rápida desde la web pública.",
        
        // 🟢 Datos por defecto para que FastAPI no rechace la petición
        tipo_persona: "natural", 
        tipo_documento: "CC", 
        cliente_documento: "0", 
        
        // 🟢 Los 3 datos reales del cliente
        cliente_nombre: form.nombreCompleto.trim(),
        cliente_email: form.correo.trim(),
        cliente_celular: form.telefono.toString()
      };

      await apiClient.post("/api/reservas/invitado", payload);

      await Swal.fire({
        icon: "success",
        title: "¡Reserva Solicitada!",
        text: `Gracias ${form.nombreCompleto.split(' ')[0]}. Nos pondremos en contacto contigo pronto.`,
        confirmButtonColor: "#0f3b2a",
      });

      closeModal();
      resetForm();
      return true;

    } catch (error) {
      console.error("Error del backend:", error);
      Swal.fire({
        icon: "error",
        title: "Ups, algo salió mal",
        text: "No pudimos registrar tu reserva. Intenta de nuevo.",
        confirmButtonColor: "#e74c3c",
      });
      return false;
    } finally {
      isSubmitting.value = false;
    }
  };

  return {
    isModalOpen, isSubmitting, form, errors, selectedDateRange, disabledDates, minDate,
    habitacionSeleccionada, openModal, closeModal, handleSubmit, resetForm,
  };
});