
# Informe de Código

## Objetivo
Documentar la arquitectura, la lista de funciones y las dependencias exactas del entorno actual.

## Pasos de ejecución
1. Preparar el entorno Python:
   - Activar el entorno virtual: `./.venv/Scripts/Activate.ps1`
   - Instalar las dependencias actuales: `python -m pip install -r Informe_de_Codigo/requirements.txt`

2. Preparar el entorno frontend:
   - Ir a la carpeta `frontend`: `cd frontend`
   - Instalar las dependencias con la versión exacta: `npm ci`

3. Iniciar servidores:
   - Backend: `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
   - Frontend: `npm run dev`

## Notas
- La API de backend estará disponible en `http://localhost:8000`.
- La interfaz de frontend quedará disponible en la URL que proporcione Vite.
- Para probar la API REST, usar `http://localhost:8000/docs`.
