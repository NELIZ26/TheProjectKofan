from backend.db.client import db
from backend.core.config import UPLOAD_DIR, ALLOWED_TYPES
from bson import ObjectId
from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool # 🟢 IMPORTANTE
import uuid, os, shutil

# Esta función la usaremos dentro del threadpool
def save_physical_file(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 🟢 Asegúrate de que esta URL coincida con tu main.py (ej: /static/uploads/...)
    return f"/static/uploads/{filename}"

def delete_physical_file(file_url: str):
    try:
        filename = file_url.split("/")[-1]
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error borrando archivo físico: {e}")

async def get_all_photos(categoria: str = None):
    query = {}
    if categoria and categoria != "todos":
        query["categoria"] = categoria 

    cursor = db.gallery.find(query).sort("created_at", -1)
    photos = []

    async for photo in cursor:
        # 🟢 SALVAVIDAS: Si no tiene fecha, no explota, solo devuelve vacío
        fecha_creacion = photo.get("created_at")
        fecha_str = fecha_creacion.isoformat() if fecha_creacion else ""

        photos.append({
            "id": str(photo["_id"]),
            "url": photo["url"],
            "titulo": photo.get("titulo", ""),
            "categoria": photo.get("categoria", "general"),
            "created_at": fecha_str,
        })

    return photos

async def upload_photo(file: UploadFile, titulo: str, categoria: str, uploader_email: str):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido. Solo JPEG, PNG o WebP.")

    # 🟢 EJECUCIÓN SEGURA PARA NO BLOQUEAR EL SERVIDOR
    url = await run_in_threadpool(save_physical_file, file)

    doc = {
        "url": url,
        "titulo": titulo,
        "categoria": categoria,
        "uploaded_by": uploader_email,
        "created_at": datetime.now(timezone.utc),
    }

    result = await db.gallery.insert_one(doc)
    return {"id": str(result.inserted_id), "url": url, "titulo": titulo, "categoria": categoria}

async def delete_photo(photo_id: str):
    photo = await db.gallery.find_one({"_id": ObjectId(photo_id)})

    if not photo:
        return False

    if "url" in photo:
        # 🟢 BORRADO FÍSICO SEGURO
        await run_in_threadpool(delete_physical_file, photo["url"])

    result = await db.gallery.delete_one({"_id": ObjectId(photo_id)})
    return result.deleted_count > 0