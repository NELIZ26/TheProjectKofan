import { defineStore } from "pinia";
import { ref, reactive, computed } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";

export const useReservaStore = defineStore("reserva", () => {
  // --- ESTADO ---
  const isModalOpen = ref(false);
  const personType = ref("natural");
  const isSubmitting = ref(false);

  const form = reactive({
    nombres: "",
    tipoDocumento: "",
    correo: "",
    fechaNacimiento: "",
    numDocumento: "",
    telefono: "",
    cantidadPersonas: "2",
    habitacion: "Cabana2",
    fechaReserva: "",
  });

  const errors = reactive({
    nombres: false,
    tipoDocumento: false,
    correo: false,
    fechaNacimiento: false,
    numDocumento: false,
    telefono: false,
    fechaReserva: false,
  });

  // --- COMPUTADOS ---
  const minDate = computed(() => new Date().toISOString().split("T")[0]);

  const labelNombres = computed(() =>
    personType.value === "juridica" ? "Razón Social" : "Nombres y Apellidos",
  );

  const placeholderNombres = computed(() =>
    personType.value === "juridica" ? "Ej: Empresa SAS" : "Ej: Juan Pérez",
  );

  const labelNumDoc = computed(() =>
    personType.value === "juridica" ? "NIT" : "Número de Documento",
  );

  // --- ACCIONES ---
  const openModal = () => {
    isModalOpen.value = true;
    clearErrors();
  };

  const closeModal = () => {
    isModalOpen.value = false;
  };

  const setPersonType = (type) => {
    personType.value = type;
  };

  const clearErrors = () => {
    Object.keys(errors).forEach((key) => (errors[key] = false));
  };

  const resetForm = () => {
    form.nombres = "";
    form.tipoDocumento = "";
    form.correo = "";
    form.fechaNacimiento = "";
    form.numDocumento = "";
    form.telefono = "";
    form.fechaReserva = "";
    form.cantidadPersonas = "2";
    form.habitacion = "Cabana2";
    personType.value = "natural";
    clearErrors();
  };

  const validateForm = () => {
    let isValid = true;
    clearErrors();

    if (!form.nombres.trim()) {
      errors.nombres = true;
      isValid = false;
    }

    if (personType.value === "natural") {
      if (!form.tipoDocumento) {
        errors.tipoDocumento = true;
        isValid = false;
      }
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!form.correo || !emailRegex.test(form.correo)) {
      errors.correo = true;
      isValid = false;
    }

    if (!form.numDocumento) {
      errors.numDocumento = true;
      isValid = false;
    }
    if (!form.telefono) {
      errors.telefono = true;
      isValid = false;
    }
    if (!form.fechaReserva) {
      errors.fechaReserva = true;
      isValid = false;
    }

    return isValid;
  };

  // --- ENVÍO CON BACKEND REAL + WHATSAPP ---
  const handleSubmit = async () => {
    if (!validateForm()) {
      Swal.fire({
        icon: "error",
        title: "Formulario Incompleto",
        text: "Por favor, revisa los campos marcados en rojo.",
        confirmButtonColor: "#e74c3c",
      });
      return;
    }

    isSubmitting.value = true;

    Swal.fire({
      title: "Procesando Reserva...",
      text: "Estamos registrando tu solicitud",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    try {
      // Llamada real al backend
      await apiClient.post("/reservas", {
        nombres: form.nombres,
        tipo_documento: form.tipoDocumento,
        correo: form.correo,
        fecha_nacimiento: form.fechaNacimiento,
        num_documento: form.numDocumento,
        telefono: form.telefono,
        cantidad_personas: form.cantidadPersonas,
        habitacion: form.habitacion,
        fecha_reserva: form.fechaReserva,
        tipo_persona: personType.value,
      });

      // Armar mensaje de WhatsApp
      const telefonoHotel = "573124225925";
      const mensajeWA =
        `¡Hola Ecohotel Kofán! 🌿%0A` +
        `Me gustaría confirmar una reserva:%0A%0A` +
        `👤 *Nombre:* ${form.nombres}%0A` +
        `🆔 *Doc:* ${form.numDocumento}%0A` +
        `🏨 *Alojamiento:* ${form.habitacion}%0A` +
        `👥 *Huéspedes:* ${form.cantidadPersonas}%0A` +
        `📅 *Check-In:* ${form.fechaReserva}%0A%0A` +
        `Espero instrucciones de pago.`;

      await Swal.fire({
        icon: "success",
        title: "¡Solicitud Registrada!",
        text: `Gracias ${form.nombres}, ahora te redirigiremos a WhatsApp para finalizar tu pago.`,
        confirmButtonColor: "#0f3b2a",
        confirmButtonText: "Ir a WhatsApp 💬",
      });

      window.open(`https://wa.me/${telefonoHotel}?text=${mensajeWA}`, "_blank");

      closeModal();
      resetForm();

    } catch (error) {
      // Manejo de errores del backend
      const msg =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "No pudimos registrar tu reserva. Intenta de nuevo.";

      Swal.fire({
        icon: "error",
        title: "Error al Reservar",
        text: msg,
        confirmButtonColor: "#e74c3c",
      });
    } finally {
      isSubmitting.value = false;
    }
  };

  return {
    isModalOpen,
    isSubmitting,
    personType,
    form,
    errors,
    minDate,
    labelNombres,
    placeholderNombres,
    labelNumDoc,
    openModal,
    closeModal,
    setPersonType,
    handleSubmit,
    resetForm,
  };
});