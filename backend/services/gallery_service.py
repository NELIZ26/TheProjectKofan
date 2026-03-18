from backend.db.client import db
from backend.core.config import UPLOAD_DIR, ALLOWED_TYPES
from bson import ObjectId
from datetime import datetime, timezone
from fastapi import UploadFile, HTTPException
import uuid, os, shutil


async def get_all_photos(categoria: str = None):
    query = {}
    if categoria and categoria != "todos":
        query["categoria"] = categoria

    cursor = db.gallery.find(query).sort("created_at", -1)
    photos = []

    async for photo in cursor:
        photos.append({
            "id": str(photo["_id"]),
            "url": photo["url"],
            "titulo": photo.get("titulo", ""),
            "categoria": photo.get("categoria", "general"),
            "created_at": photo["created_at"].isoformat(),
        })

    return photos


async def upload_photo(file: UploadFile, titulo: str, categoria: str, uploader_email: str):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido. Solo JPEG, PNG o WebP.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    url = f"/static/images/{filename}"

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

    # Eliminar archivo físico
    filepath = photo["url"].replace("/static/", "", 1)
    full_path = os.path.join(os.path.dirname(UPLOAD_DIR), filepath)
    if os.path.exists(full_path):
        os.remove(full_path)

    result = await db.gallery.delete_one({"_id": ObjectId(photo_id)})
    return result.deleted_count > 0