# Análisis de Funciones

Este documento enumera las funciones identificadas en el backend y frontend del proyecto, con comentarios técnicos sobre las más críticas.

## Backend (FastAPI + MongoDB)

### Funciones críticas y su lógica de negocio

- `create_booking_service`: valida `habitacion_id`, asegura que la habitación exista, convierte fechas a UTC y evita solapamiento de reservas en MongoDB. Inserta la reserva con estado `pendiente` y la vincula al usuario autenticado cuando aplica.
- `update_booking_status_service`: actualiza el estado de la reserva y persiste los cambios en MongoDB. Altera el flujo de datos notificando tanto al cliente como al administrador, construyendo mensajes dinámicos según el nuevo estado e incluyendo datos contextualizados de habitación y cliente.
- `get_user_bookings_service`: agrega datos de habitación mediante `$lookup` con la colección `rooms`, normaliza fechas y genera la respuesta de `mis-reservas` para el usuario autenticado. Este flujo garantiza que la vista del cliente reciba información de habitación limpia y legible.
- `get_all_bookings_service`: aplica filtros por estados, paginación y agrega datos de habitación y cliente para el panel administrativo. Produce un resumen de ocupación y métricas clave para dashboard, lo que facilita la atención operativa y el seguimiento de reservas pendientes.
- `get_rooms` y `update_room`: implementan búsqueda avanzada con filtros sobre nombre, disponibilidad y rango de precio. `update_room` registra cambios significativos y genera auditoría para mantener trazabilidad de modificaciones en la administración.
- `hash_password` / `verify_password`: encapsulan el estándar de seguridad `bcrypt`, protegiendo contraseñas y evitando comparar valores en texto plano.
- `create_access_token` / `create_refresh_token`: generan JWT con expiración y firma segura, simplificando la gestión de sesiones y habilitando rutas protegidas.
- `get_current_user` / `required_admin`: decodifican el token JWT y aplican autorización por rol. Estas dependencias sostienen el flujo de seguridad: cada petición autenticada recupera al usuario, y las rutas críticas requieren `admin`.

### Flujo de reserva y rutas cliente/admin

- El frontend público envía reservas a `/api/reservas/invitado` con `FormData` cuando el usuario no está autenticado. El backend solo guarda la reserva y el comprobante, sin vincularla a un `cliente_id`.
- Las reservas de usuarios autenticados se envían a `/api/reservas/` y usan `Depends(get_current_user)` para obtener el `user_id` desde el JWT. La reserva se asocia al cliente y luego puede consultarse desde `mis-reservas`.
- La ruta `/api/reservas/mis-reservas` es de uso exclusivo del cliente autenticado y devuelve solo sus reservas; el servicio usa `cliente_id` para filtrar y aplicar joins con `rooms`.
- Las rutas administrativas como `/api/reservas/admin/todas`, `PATCH /api/reservas/{reserva_id}/estado` y `PUT /api/reservas/{reserva_id}/detalles` requieren `required_admin`, bloqueando acceso a usuarios sin el rol `admin`.
- El backend separa claramente dos dominios: el de cliente (`mis-reservas`, creación de reservas públicas y autenticadas) y el de administración (`all bookings`, cambio de estado, actualización de detalles), lo que mejora la mantenibilidad y seguridad.

### Diagrama de flujo del proceso de reserva

1. Usuario selecciona habitación y fechas en frontend.
2. Frontend construye `FormData` e invoca:
   - `/api/reservas/invitado` si no hay token.
   - `/api/reservas/` si hay token válido.
3. Backend valida datos y fechas, y ejecuta `create_booking_service`.
4. `create_booking_service` verifica disponibilidad, convierte fechas a UTC y guarda la reserva en MongoDB.
5. Si es usuario autenticado, la reserva se asocia a `cliente_id`; si es invitado, queda sin vínculo de usuario.
6. El cliente puede consultar sus reservas desde `/api/reservas/mis-reservas`.
7. El administrador usa `/api/reservas/admin/todas` y puede cambiar estado o detalles con rutas protegidas por `required_admin`.

### Listado de funciones en backend

#### `backend\core\security.py`
- Línea 13: `hash_password`
- Línea 18: `verify_password`
- Línea 21: `create_access_token`
- Línea 27: `create_refresh_token`

#### `backend\doc_backend.py`
- Línea 3: `generar_doc_backend`

#### `backend\models\user_models.py`
- Línea 3: `user_entity`

#### `backend\schemas\config_schema.py`
- Línea 1: `site_config_schema`

#### `backend\schemas\gallery_schema.py`
- Línea 3: `image_schema`
- Línea 15: `images_schema`

#### `backend\schemas\invoice_schema.py`
- Línea 1: `invoice_schema`
- Línea 21: `invoices_schema`

#### `backend\schemas\room_schema.py`
- Línea 1: `room_schema`
- Línea 23: `rooms_schema`

#### `backend\services\gallery_service.py`
- Línea 10: `save_physical_file`
- Línea 22: `delete_physical_file`

#### `backend\services\media_service.py`
- Línea 9: `save_image`
- Línea 28: `save_multiple`
- Línea 51: `delete_image`

#### `backend\services\room_service.py`
- Línea 15: `is_valid_object_id`

## Frontend (Vue 3 + Vite + Pinia)

### Funciones críticas y su lógica de negocio

- `handleSubmit` en `frontend/src/stores/reserva.js`: valida el formulario, construye `FormData` para incluir comprobante de pago, selecciona el endpoint según el contexto de autenticación y maneja la UX de envío con SweetAlert.
- `fetchDisabledDates` en `frontend/src/stores/reserva.js`: consume fechas ocupadas desde la API, transforma los intervalos y adapta el check-out para que el último día quede libre en el calendario.
- `handleFileUpload` en `frontend/src/stores/reserva.js`: normaliza archivos de comprobante y habilita vista previa de imagen o PDF.
- `openModal` / `closeModal` en `frontend/src/stores/reserva.js`: controlan el estado modal, reinician formularios y preservan la consistencia de datos entre vistas.
- `cambiar_estado_reserva` en el backend y `actualizarEstado` en `frontend/src/views/admin/BookingsManager.vue`: representan el flujo de aprobación de reservas desde el panel admin hacia el servicio de backend.
- `getBrandColor` en múltiples componentes: centraliza la obtención de variables CSS para mantener coherencia visual en la capa de presentación.

### Listado de funciones en frontend

#### `frontend\src\components\FormularioRegistro.vue`
- Línea 21: `getBrandColor`
- Línea 33: `resetForm`
- Línea 64: `procesarFormulario`

#### `frontend\src\components\ImageUploader.vue`
- Línea 25: `procesarArchivos`
- Línea 50: `triggerFileInput`
- Línea 54: `quitarFotoNueva`
- Línea 61: `emitirCambios`
- Línea 67: `reset`

#### `frontend\src\components\ModalEdicionReserva.vue`
- Línea 34: `agregarConsumo`
- Línea 39: `quitarConsumo`
- Línea 44: `recalcularTotal`
- Línea 116: `agregarAcompanante`
- Línea 126: `quitarAcompanante`
- Línea 225: `cerrar`

#### `frontend\src\components\ModalFactura.vue`
- Línea 39: `cerrar`
- Línea 67: `formatoDinero`

#### `frontend\src\components\ModalUsuario.vue`
- Línea 13: `propagarGuardado`

#### `frontend\src\components\Navbar.vue`
- Línea 14: `handleScroll`
- Línea 27: `logout`

#### `frontend\src\components\ReservaModal.vue`
- Línea 13: `actualizarColumnas`

#### `frontend\src\components\RoomCalendarModal.vue`
- Línea 8: `getBrandColor`
- Línea 28: `actualizarColumnas`
- Línea 167: `onDayClick`
- Línea 171: `avanzarPaso`
- Línea 257: `cerrar`

#### `frontend\src\components\RoomCard.vue`
- Línea 45: `formatPrice`
- Línea 49: `handleReservar`
- Línea 51: `siguienteFoto`
- Línea 57: `anteriorFoto`
- Línea 63: `abrirLightbox`
- Línea 64: `cerrarLightbox`

#### `frontend\src\components\RoomHistoryCard.vue`
- Línea 23: `formatTime`

#### `frontend\src\components\RoomHistoryModal.vue`
- Línea 36: `toggleRow`
- Línea 45: `formatTime`
- Línea 51: `nextPage`
- Línea 52: `prevPage`

#### `frontend\src\components\form\PasswordInput.vue`
- Línea 55: `toggle`

#### `frontend\src\layouts\AdminLayout.vue`
- Línea 29: `handleLogout`

#### `frontend\src\router\index.js`
- Línea 4: `PublicLayout`
- Línea 5: `LandingPortal`
- Línea 6: `HomeView`
- Línea 7: `AboutUs`
- Línea 8: `ContactUs`
- Línea 9: `PhotoGallery`
- Línea 10: `Catalog`
- Línea 11: `ConfiguracionAdmin`
- Línea 13: `AppLayout`
- Línea 14: `AdminLayout`
- Línea 15: `AuthLayout`

#### `frontend\src\stores\auth.js`
- Línea 20: `login`
- Línea 32: `logout`

#### `frontend\src\stores\reserva.js`
- Línea 7: `getBrandColor`
- Línea 60: `handleFileUpload`
- Línea 120: `closeModal`
- Línea 125: `clearErrors`
- Línea 129: `resetForm`
- Línea 147: `validateForm`
- Línea 181: `formatLocal`
- Línea 253: `removerComprobante`

#### `frontend\src\views\ServiceSelection.vue`
- Línea 56: `goToHospedaje`

#### `frontend\src\views\admin\AdminHeader.vue`
- Línea 14: `getBrandColor`
- Línea 22: `handleLogout`

#### `frontend\src\views\admin\BookingsManager.vue`
- Línea 41: `getBrandColor`
- Línea 85: `cambiarPestana`
- Línea 90: `cambiarPagina`
- Línea 166: `actualizarEstado`
- Línea 230: `eliminarReserva`
- Línea 247: `getBadgeClass`
- Línea 265: `getBadgeIcon`
- Línea 286: `abrirModalEdicion`

#### `frontend\src\views\admin\DashboardView.vue`
- Línea 34: `normalizarAccion`

#### `frontend\src\views\admin\GalleryManager.vue`
- Línea 19: `fotoUrl`
- Línea 34: `cancelarUpload`
- Línea 108: `cambiarFiltro`

#### `frontend\src\views\admin\RoomsManager.vue`
- Línea 32: `getBrandColor`
- Línea 90: `procesarArchivos`
- Línea 106: `handleFilesUpload`
- Línea 111: `onDrop`
- Línea 116: `triggerFileInput`
- Línea 120: `quitarFotoNueva`
- Línea 125: `resetForm`
- Línea 136: `prepararCreacion`
- Línea 138: `prepararEdicion`
- Línea 230: `manejarErrorImagen`
- Línea 238: `seleccionarPrincipal`
- Línea 242: `abrirCalendario`
- Línea 248: `cerrarCalendario`

#### `frontend\src\views\admin\UsersManager.vue`
- Línea 44: `cambiarPagina`
- Línea 49: `abrirNuevo`
- Línea 54: `abrirEdicion`

#### `frontend\src\views\app\BookingDetail.vue`
- Línea 27: `volver`

#### `frontend\src\views\app\BookingsView.vue`
- Línea 78: `filtrarLista`
- Línea 97: `limpiarFiltros`
- Línea 116: `formatFecha`
- Línea 124: `getNombreEstadoVisual`
- Línea 129: `getBadgeClass`
- Línea 143: `getBadgeIcon`

#### `frontend\src\views\app\NotificationsView.vue`
- Línea 49: `resolverIconoAviso`

#### `frontend\src\views\app\ProfileView.vue`
- Línea 33: `resolverIconoAviso`

#### `frontend\src\views\app\SettingsView.vue`
- Línea 9: `getBrandColor`

#### `frontend\src\views\app\SidebarView.vue`
- Línea 23: `handleLogout`

#### `frontend\src\views\auth\Register.vue`
- Línea 15: `getBrandColor`

#### `frontend\src\views\public\Catalog.vue`
- Línea 88: `obtenerListaHabitaciones`
- Línea 94: `obtenerEstadoActivo`
- Línea 103: `normalizarTipoAlojamiento`
- Línea 151: `filtrarPorTipo`

#### `frontend\src\views\public\ContactUs.vue`
- Línea 242: `getBrandColor`
- Línea 255: `enviarFormulario`

#### `frontend\src\views\public\LandingPortal.vue`
- Línea 56: `goToHospedaje`

#### `frontend\src\views\public\PhotosGallery.vue`
- Línea 125: `fotoUrl`
- Línea 140: `cambiarFiltro`
- Línea 145: `abrirLightbox`
- Línea 152: `cerrarLightbox`
- Línea 158: `navLightbox`
- Línea 164: `onKeydown`
