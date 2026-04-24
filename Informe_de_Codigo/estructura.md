
# Estructura del Proyecto

## Arquitectura general
- Arquitectura en tres capas: presentación (frontend), lógica de negocio y API (backend), persistencia (MongoDB).
- Roles: `admin` y `cliente` con protecciones específicas en rutas y servicios.
- Backend usa FastAPI con autenticación JWT y dependencias de seguridad en `backend/dependencies/auth.py`.
- Frontend usa Vue 3, Vite y Pinia para estado, con componentes y vistas especializadas para administración y usuario final.

## Carpetas principales
- `/backend`: servidor REST, validaciones, servicios, routers, esquemas y seguridad.
- `/frontend`: aplicación Vue, rutas, layouts, componentes, stores y servicios API.
- `/.venv`: entorno virtual Python con las dependencias instaladas para backend.
- `/testing`: pruebas unitarias/end-to-end y configuración de entorno de pruebas.

## Backend
- `backend/main.py`: arranque de FastAPI.
- `backend/routers`: definición de endpoints por dominio (usuarios, reservas, habitaciones, config, facturas, notificaciones, galería, admin).
- `backend/services`: lógica de negocio centralizada, especialmente reservas, habitaciones, usuarios, notificaciones y archivos.
- `backend/dependencies/auth.py`: validación de JWT y autorización de administrador.
- `backend/core/security.py`: hashing de contraseñas y generación de tokens de acceso/refresh.
- `backend/db/client.py`: cliente de MongoDB.

## Frontend
- `frontend/src/router/index.js`: rutas públicas, autenticadas y administrativas.
- `frontend/src/stores`: gestión de autenticación, configuración, galería y reservas.
- `frontend/src/views`: vistas de cliente y admin con formularios, tablas y paneles de control.
- `frontend/src/components`: componentes reutilizables de UI y modales de reserva/factura.

## Entorno virtual
- Python 3.14 en `/.venv`.
- Dependencias backend definidas en `Informe_de_Codigo/requirements.txt`.
- Dependencias frontend definidas en `Informe_de_Codigo/package.json` con versiones exactas según `frontend/package-lock.json`.
