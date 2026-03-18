import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import admin, auth, earnings, register, users, bookings, rooms, bookings_sin_auth, gallery

app = FastAPI(
    title="Ecohotel Kofán API",
    version="1.0.0",
)

# 1. MIDDLEWARE — siempre primero
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ARCHIVOS ESTÁTICOS — después del middleware
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)  # Crea la carpeta si no existe
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 3. ROUTERS — siempre al final
app.include_router(auth.router)
app.include_router(register.router)
app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(bookings_sin_auth.router)
app.include_router(rooms.router)
app.include_router(gallery.router)
app.include_router(earnings.router)
app.include_router(admin.router)