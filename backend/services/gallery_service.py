from backend.db.client import db
from backend.core.config import UPLOAD_DIR, ALLOWED_TYPES
from bson import ObjectId
from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool # 🟢 IMPORTANTE
import uuid, os, shutil

LEGACY_IMAGES_DIR = os.path.join(os.path.dirname(UPLOAD_DIR), "images")

def build_gallery_file_url(stored_url: str | None) -> str | None:
    if not stored_url:
        return None

    filename = os.path.basename(stored_url)
    upload_public_url = f"/static/uploads/{filename}"
    legacy_public_url = f"/static/images/{filename}"
    upload_path = os.path.join(UPLOAD_DIR, filename)
    legacy_path = os.path.join(LEGACY_IMAGES_DIR, filename)

    if stored_url.startswith("/static/uploads/") and os.path.exists(upload_path):
        return upload_public_url

    if stored_url.startswith("/static/images/") and os.path.exists(legacy_path):
        return legacy_public_url

    if os.path.exists(upload_path):
        return upload_public_url

    if os.path.exists(legacy_path):
        return legacy_public_url

    return upload_public_url

# Esta función la usaremos dentro del threadpool
def save_physical_file(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return f"/static/uploads/{filename}"

def delete_physical_file(file_url: str):
    try:
        filename = file_url.split("/")[-1]
        possible_paths = [
            os.path.join(UPLOAD_DIR, filename),
            os.path.join(LEGACY_IMAGES_DIR, filename),
        ]

        for filepath in possible_paths:
            if os.path.exists(filepath):
                os.remove(filepath)
                break
    except Exception as e:
        print(f"Error borrando archivo físico: {e}")

async def get_all_photos(categoria: str = None):
    query = {}
    if categoria and categoria != "todos":
        query["categoria"] = categoria # 🟢 Todo en español para consistencia

    cursor = db.gallery.find(query).sort("created_at", -1)
    photos = []

    async for photo in cursor:
        created_at = photo.get("created_at")
        photos.append({
            "id": str(photo["_id"]),
            "url": build_gallery_file_url(photo.get("url")),
            "titulo": photo.get("titulo", ""),
            "categoria": photo.get("categoria", "general"),
            "created_at": created_at.isoformat() if created_at else None,
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