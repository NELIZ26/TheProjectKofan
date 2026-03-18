import shutil
import uuid
from pathlib import Path

from bson import ObjectId
from datetime import datetime, timezone
from backend.db.client import db 
from backend.schemas.room_schema import room_schema, rooms_schema
from backend.core.config import UPLOAD_DIR
from fastapi import UploadFile

collection = db.rooms

# --- CREATE ---
async def create_room(data: dict, user_email: str):
    now = datetime.now(timezone.utc)

    data["created_by"] = user_email
    data["updated_by"] = user_email
    data["created_at"] = now
    data["updated_at"] = now
    
    # Por defecto, una habitación nueva debe estar disponible para el dashboard
    if "is_available" not in data:
        data["is_available"] = True

    # Motor requiere await para insertar
    result = await collection.insert_one(data)
    
    # Buscamos el objeto recién creado para devolverlo con el esquema
    new_room = await collection.find_one({"_id": result.inserted_id})
    return room_schema(new_room)

# --- CREATE WITH IMAGES ---
async def create_room_with_images(data: dict, images: list[str], user_email: str):
    data["images"] = images

    if images:
        data["main_image"] = images[0]

    # Llamamos a la función asíncrona de arriba con await
    return await create_room(data, user_email)

# --- GET ONE ---
async def get_room(room_id: str):
    # Convertimos el string a ObjectId y esperamos el resultado
    room = await collection.find_one({"_id": ObjectId(room_id)})
    if not room:
        return None # Es mejor retornar None para que el router maneje el 404
    return room_schema(room)

# --- LIST WITH ADVANCED FILTER ---
async def get_rooms(page: int, limit: int, filters: dict):
    skip = (page - 1) * limit
    query = {}

    # Lógica de filtros (se mantiene igual, es solo construcción de diccionario)
    if filters.get("name"):
        query["name"] = {"$regex": filters["name"], "$options": "i"}
    if filters.get("active") is not None:
        query["active"] = filters["active"]
    if filters.get("min_price") is not None:
        query.setdefault("price", {})["$gte"] = filters["min_price"]
    if filters.get("max_price") is not None:
        query.setdefault("price", {})["$lte"] = filters["max_price"]

    # Motor usa cursores. Para convertirlos a lista usamos to_list()
    cursor = collection.find(query).skip(skip).limit(limit)
    rooms_list = await cursor.to_list(length=limit)
    
    # Contamos los documentos de forma asíncrona
    total = await collection.count_documents(query)

    return {
        "data": rooms_schema(rooms_list), # Asegúrate que rooms_schema acepte la lista
        "total": total,
        "page": page,
        "limit": limit,
    }

# --- UPDATE ---
async def update_room(room_id: str, data: dict, user_email: str):
    data["updated_by"] = user_email
    data["updated_at"] = datetime.now(timezone.utc)

    # Actualizamos con await
    await collection.update_one({"_id": ObjectId(room_id)}, {"$set": data})
    
    # Retornamos la habitación actualizada
    return await get_room(room_id)

# --- REMOVE IMAGE FROM ROOM ---
async def remove_room_image(room_id: str, url: str, user_email: str):
    room = await get_room(room_id)
    if not room:
        return None

    images = room.get("images", [])
    if url in images:
        images.remove(url)

    update_data = {"images": images}
    # Si borramos la imagen principal, ponemos la siguiente o None
    if room.get("main_image") == url:
        update_data["main_image"] = images[0] if images else None

    return await update_room(room_id, update_data, user_email)

# --- DELETE ---
async def delete_room(room_id: str):
    result = await collection.delete_one({"_id": ObjectId(room_id)})
    if result.deleted_count == 0:
        return False
    return True



async def add_room_images_to_db(room_id: str, new_urls: list):
    try:
        result = await collection.update_one(
            {"_id": ObjectId(room_id)},
            {"$push": {"images": {"$each": new_urls}}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error al actualizar array en MongoDB: {e}")
        return False


# --- FUNCIÓN PARA GUARDAR MÚLTIPLES IMÁGENES ---
def save_multiple(files: list[UploadFile]) -> list[str]:
    urls = []
    for file in files:
        try:
            # Generamos el nombre: UUID_NombreOriginal.ext
            # Esto es lo que tú ya tenías en la base de datos
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            
            # Usamos el UPLOAD_DIR que viene de tu config
            # Aseguramos que sea un objeto Path para usar el operador /
            file_path = Path(UPLOAD_DIR) / unique_filename
            
            # Guardamos físicamente
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Devolvemos la URL con el formato que ya usa Kofán
            urls.append(f"/static/images/{unique_filename}")
        except Exception as e:
            print(f"Error al guardar archivo {file.filename}: {e}")
            
    return urls



