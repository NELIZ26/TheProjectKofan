import os
import uuid
import shutil
from pathlib import Path
from backend.core.config import UPLOAD_DIR, ALLOWED_TYPES
from fastapi import UploadFile, HTTPException


def save_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Limpiamos el nombre para que sea 100% seguro
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}" # Usamos .hex para quitar los guiones del UUID
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 🟢 AJUSTE: Si en main.py montaste UPLOAD_DIR como "/static/uploads",
    # la URL que guardes en la base de datos DEBE apuntar ahí mismo.
    return f"/static/uploads/{filename}"


def save_multiple(files: list[UploadFile]) -> list[str]:
    urls = []
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    for file in files:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

        # 🟢 FIX: Aplicamos la misma limpieza estricta que en save_image
        # Eliminamos por completo el nombre original del archivo
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 🟢 AJUSTE: Misma corrección de ruta
        urls.append(f"/static/uploads/{filename}")

    return urls


def delete_image(image_url: str):
    """
    Toma la URL de la base de datos (ej: /static/uploads/archivo.png)
    y elimina el archivo físico del disco duro.
    """
    if not image_url:
        return

    try:
        # Extraemos solo el nombre del archivo de la URL
        filename = image_url.split("/")[-1]
        
        # Construimos la ruta física real usando tu UPLOAD_DIR
        file_path = Path(UPLOAD_DIR) / filename
        
        # Verificamos si el archivo existe antes de intentar borrarlo
        if file_path.exists():
            file_path.unlink() 
            print(f"✅ Imagen eliminada del disco: {filename}")
        else:
            print(f"⚠️ El archivo no existe en el disco: {file_path}")
            
    except Exception as e:
        print(f"❌ Error al intentar eliminar el archivo físico {image_url}: {e}")