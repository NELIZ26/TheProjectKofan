from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import admin, auth, earnings, register, users, bookings, rooms, config, gallery, invoices
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from backend.services.task_service import cancelar_reservas_vencidas
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from fastapi.staticfiles import StaticFiles
from backend.core.config import UPLOAD_DIR

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cancelar_reservas_vencidas, 'interval', hours=24)
    scheduler.start()
    print("⏳ Motor de tareas automáticas iniciado.")
    
    yield
    
    scheduler.shutdown()
    print("🛑 Motor de tareas automáticas detenido.")

app = FastAPI(lifespan=lifespan)

app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="static_uploads")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],        
    allow_headers=["*"],        
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(register.router)
app.include_router(earnings.router)
app.include_router(rooms.router)
app.include_router(admin.router)
app.include_router(config.router)
app.include_router(gallery.router)
app.include_router(invoices.router)