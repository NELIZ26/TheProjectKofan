import os
from pathlib import Path
from dotenv import load_dotenv

# Cargamos el .env desde la carpeta backend/
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# --- SEGURIDAD JWT ---
SECRET = os.getenv("SECRET_KEY", "mysecretkey")  # Definir SECRET_KEY en .env en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# --- ARCHIVOS ESTÁTICOS ---
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]