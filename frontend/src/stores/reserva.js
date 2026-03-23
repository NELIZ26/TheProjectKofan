import { defineStore } from "pinia";
import { ref, reactive, computed, watch } from "vue";
import Swal from "sweetalert2";
import apiClient from "@/api/apiClient";

export const useReservaStore = defineStore("reserva", () => {
  // --- ESTADO ---
  const isModalOpen = ref(false);
  const personType = ref("natural");
  const isSubmitting = ref(false);
  const habitacionSeleccionada = ref(null);

  const form = reactive({
    nombres: "",
    tipoDocumento: "",
    correo: "",
    numDocumento: "",
    telefono: "",
    cantidadPersonas: "2",
    habitacion: "",
    fechaReserva: "", // Check-In
    fechaSalida: "",  // Check-Out
    registrarAcompanantesAhora: false, // Switch (Toggle)
    acompanantes: [] // Array dinámico
  });

  const errors = reactive({
    nombres: false,
    tipoDocumento: false,
    correo: false,
    numDocumento: false,
    telefono: false,
    fechaReserva: false,
    fechaSalida: false, 
    habitacion: false,
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

  // --- VIGILANTE (WATCHER) PARA LOS ACOMPAÑANTES ---
  watch(() => form.cantidadPersonas, (nuevoValor) => {
    let numAcompanantes = 0;
    
    if (nuevoValor === "5+") {
      numAcompanantes = 4;
    } else {
      numAcompanantes = parseInt(nuevoValor) - 1;
    }

    if (numAcompanantes > 0) {
      while (form.acompanantes.length < numAcompanantes) {
        form.acompanantes.push({ nombre_completo: "", numero_documento: "", parentesco: "" });
      }
      if (form.acompanantes.length > numAcompanantes) {
        form.acompanantes = form.acompanantes.slice(0, numAcompanantes);
      }
    } else {
      form.acompanantes = [];
    }
  }, { immediate: true });


  // --- ACCIONES ---
  const openModal = (habitacion = null) => {
    isModalOpen.value = true;
    clearErrors();
    if (habitacion) {
      habitacionSeleccionada.value = habitacion;
      form.habitacion = habitacion.name;
    }
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
    form.numDocumento = "";
    form.telefono = "";
    form.fechaReserva = "";
    form.fechaSalida = "";
    form.cantidadPersonas = "2";
    form.habitacion = "";
    form.registrarAcompanantesAhora = false;
    
    habitacionSeleccionada.value = null;
    personType.value = "natural";
    clearErrors();
  };

  const validateForm = () => {
    let isValid = true;
    clearErrors();

    if (!form.nombres.trim()) { errors.nombres = true; isValid = false; }
    if (personType.value === "natural" && !form.tipoDocumento) { errors.tipoDocumento = true; isValid = false; }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!form.correo || !emailRegex.test(form.correo)) { errors.correo = true; isValid = false; }
    
    if (!form.numDocumento) { errors.numDocumento = true; isValid = false; }
    if (!form.telefono) { errors.telefono = true; isValid = false; }
    if (!form.habitacion) { errors.habitacion = true; isValid = false; }
    if (!form.fechaReserva) { errors.fechaReserva = true; isValid = false; }
    
    if (!form.fechaSalida || form.fechaSalida <= form.fechaReserva) { 
      errors.fechaSalida = true; 
      isValid = false; 
    }

    return isValid;
  };

  // --- ENVÍO CON BACKEND REAL (SIN WHATSAPP) ---
  const handleSubmit = async () => {
    if (!validateForm()) {
      Swal.fire({
        icon: "error",
        title: "Datos incompletos",
        text: "Por favor, revisa las fechas y los campos marcados en rojo.",
        confirmButtonColor: "#e74c3c",
      });
      return false; 
    }

    isSubmitting.value = true;

    // 1. CALCULAR DÍAS DE ESTADÍA Y MONTO TOTAL (Requerido por FastAPI)
    const checkIn = new Date(form.fechaReserva);
    const checkOut = new Date(form.fechaSalida);
    const diferenciaMilisegundos = checkOut.getTime() - checkIn.getTime();
    const diasEstadia = Math.ceil(diferenciaMilisegundos / (1000 * 60 * 60 * 24)) || 1;
    
    const montoCalculado = habitacionSeleccionada.value.price * diasEstadia;

    Swal.fire({
      title: "Procesando Reserva...",
      text: "Estamos registrando tu solicitud en el sistema",
      allowOutsideClick: false,
      didOpen: () => { Swal.showLoading(); },
    });

    try {
      // 2. ARMAR EL PAYLOAD PARA FASTAPI
      const payload = {
        habitacion_id: habitacionSeleccionada.value.id || habitacionSeleccionada.value._id, 
        fecha_entrada: form.fechaReserva,
        fecha_salida: form.fechaSalida,
        monto_total: montoCalculado,
        acompanantes: form.registrarAcompanantesAhora ? form.acompanantes : [], 
        observaciones: `Reserva web para ${form.cantidadPersonas} personas.`,
        
        tipo_persona: personType.value,
        tipo_documento: personType.value === "juridica" ? "NIT" : form.tipoDocumento,
        cliente_documento: form.numDocumento.toString(),
        cliente_nombre: form.nombres,
        cliente_email: form.correo,
        cliente_celular: form.telefono.toString()
      };

      // 3. LLAMADA A LA RUTA DE INVITADOS
      await apiClient.post("/api/reservas/invitado", payload);

      // 4. MENSAJE DE ÉXITO Y CIERRE (Todo queda en el admin)
      await Swal.fire({
        icon: "success",
        title: "¡Reserva Solicitada!",
        text: `Gracias ${form.nombres}. Tu reserva quedó en estado Pendiente. Pronto te contactaremos para confirmar.`,
        confirmButtonColor: "#0f3b2a",
        confirmButtonText: "Entendido",
      });

      closeModal();
      resetForm();

      return true;

    } catch (error) {
      console.error("Error del backend:", error);
      const msg = error.response?.data?.detail || "No pudimos registrar tu reserva. Verifica los datos e intenta de nuevo.";

      Swal.fire({
        icon: "error",
        title: "Error al Reservar",
        text: msg,
        confirmButtonColor: "#e74c3c",
      });
      return false;
    } finally {
      isSubmitting.value = false;
    }
  };

  // 🟢 ESTO ERA LO QUE FALTABA (EL RETURN)
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
    habitacionSeleccionada,
    openModal,
    closeModal,
    setPersonType,
    handleSubmit,
    resetForm,
  };
});