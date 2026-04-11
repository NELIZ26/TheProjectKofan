# 🧪 Suite de Pruebas - Ecohotel Kofán

Esta carpeta contiene la base de pruebas para cumplir los estándares de calidad del proyecto **Ecohotel Kofán**.

## Estructura

- `conftest.py`: fixtures globales de `pytest` y base de datos MongoDB de prueba en memoria.
- `test_backend.py`: pruebas unitarias e integración del backend FastAPI.
- `test_frontend.js`: pruebas de lógica de frontend con **Vitest**.
- `test_e2e.spec.js`: flujo end-to-end con **Playwright**.
- `vitest.config.js`: configuración de Vitest para Vue 3.
- `playwright.config.js`: configuración de Playwright.
- `requirements-test.txt`: dependencias Python sugeridas para testing.

---

# 1. Instalación de dependencias

## 1.1 Backend (Python)

Desde la raíz del proyecto:

```bash
cd L:\SENA\WorkspaceD
pip install -r testing/requirements-test.txt
```

Si desea instalar manualmente:

```bash
pip install pytest pytest-asyncio httpx mongomock-motor pytest-cov
```

## 1.2 Frontend (Vitest + Playwright)

Desde la carpeta `frontend`:

```bash
cd L:\SENA\WorkspaceD\frontend
npm install -D vitest @vue/test-utils jsdom @playwright/test
npx playwright install
```

---

# 2. Cómo ejecutar las pruebas

## 2.1 Pruebas de backend

Desde la raíz del proyecto:

```bash
cd L:\SENA\WorkspaceD
pytest testing/test_backend.py -q
```

Para ver cobertura:

```bash
pytest testing/test_backend.py --cov=backend --cov-report=term-missing
```

## 2.2 Pruebas de frontend

Desde la raíz del proyecto:

```bash
cd L:\SENA\WorkspaceD
npx vitest --config testing/vitest.config.js run
```

## 2.3 Pruebas End-to-End (E2E)

Asegúrese de tener el frontend disponible en `http://127.0.0.1:5173`.

Luego ejecute:

```bash
cd L:\SENA\WorkspaceD
npx playwright test --config testing/playwright.config.js
```

---

# 3. Qué valida esta suite

## Backend

- **Auth**
  - login exitoso
  - rechazo por contraseña incorrecta

- **Usuarios**
  - creación por administrador
  - lectura de perfil con `GET /users/me`
  - edición con `PATCH /users/update-me`

- **Reservas**
  - creación correcta de reserva
  - bloqueo de reservas con fechas duplicadas en la misma habitación

- **Habitaciones**
  - listado general
  - validación de visibilidad pública según `active` e `is_available`

## Frontend

- evento de reserva en `RoomCard.vue`
- cálculo del total y anticipo en el flujo de reserva
- disponibilidad de variables CSS (`--k-apple`, `--k-forest`, `--k-sky`)

## E2E

- usuario entra al catálogo
- visualiza habitaciones
- abre el flujo de reserva
- diligencia el formulario
- recibe confirmación

---

# 4. Consideraciones técnicas importantes

## MongoDB de prueba

Los tests de backend **no usan la base real de MongoDB Atlas**.

Se emplea una base de datos simulada en memoria con `mongomock-motor`, para evitar ensuciar los datos de producción o desarrollo.

## Mapeo `id` vs `_id`

La suite fue escrita respetando el mapeo actual del proyecto:

- MongoDB guarda `_id`
- la API expone normalmente `id`
- en reservas y habitaciones, los tests convierten explícitamente `ObjectId` a `str()` cuando corresponde

Esto reduce errores típicos de integración como:

- `ObjectId is not JSON serializable`
- inconsistencia entre `id` y `_id`
- referencias rotas entre `rooms`, `bookings` y `users`

---

# 5. Recomendación para calidad SENA

Antes de la entrega final, se recomienda ejecutar esta secuencia:

```bash
pytest testing/test_backend.py --cov=backend
npx vitest --config testing/vitest.config.js run
npx playwright test --config testing/playwright.config.js
```

Y conservar evidencia de:

- resultados en consola,
- capturas del flujo E2E,
- cobertura mínima alcanzada.
