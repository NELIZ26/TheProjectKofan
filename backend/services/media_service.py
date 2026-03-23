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

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/static/images/{filename}"

def save_multiple(files: list[UploadFile]) -> list[str]:
    urls = []

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    for file in files:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        urls.append(f"/static/images/{filename}")

    return urls



def delete_image(image_url: str):
    """
    Toma la URL de la base de datos (/static/images/archivo.png)
    y elimina el archivo físico del disco duro.
    """
    if not image_url:
        return

    try:
        # 1. Extraemos solo el nombre del archivo de la URL
        # Ejemplo: de "/static/images/1234_foto.png" sacamos "1234_foto.png"
        filename = image_url.split("/")[-1]
        
        # 2. Construimos la ruta física real usando tu UPLOAD_DIR
        file_path = Path(UPLOAD_DIR) / filename
        
        # 3. Verificamos si el archivo existe antes de intentar borrarlo
        if file_path.exists():
            file_path.unlink() # Este es el comando que elimina físicamente el archivo
            print(f"✅ Imagen eliminada del disco: {filename}")
        else:
            print(f"⚠️ El archivo no existe en el disco: {file_path}")
            
    except Exception as e:
        print(f"❌ Error al intentar eliminar el archivo físico {image_url}: {e}")