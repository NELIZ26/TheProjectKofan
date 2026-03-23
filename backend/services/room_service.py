import shutil
import uuid
from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId  # 🟢 NUEVO: Para evitar que la app explote con IDs falsos
from datetime import datetime, timezone
from backend.db.client import db 
from backend.schemas.room_schema import room_schema, rooms_schema
from backend.core.config import UPLOAD_DIR
from fastapi import UploadFile

collection = db.rooms

# --- HELPER: Validar ObjectId ---
def is_valid_object_id(id_str: str) -> bool:
    try:
        ObjectId(id_str)
        return True
    except InvalidId:
        return False

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

    if "active" not in data:
        data["active"] = True

    result = await collection.insert_one(data)
    new_room = await collection.find_one({"_id": result.inserted_id})
    return room_schema(new_room)

# --- CREATE WITH IMAGES ---
async def create_room_with_images(data: dict, images: list[str], user_email: str):
    data["images"] = images

    if images:
        data["main_image"] = images[0]

    return await create_room(data, user_email)

# --- GET ONE ---
async def get_room(room_id: str):
    if not is_valid_object_id(room_id):
        return None

    room = await collection.find_one({"_id": ObjectId(room_id)})
    if not room:
        return None 
    return room_schema(room)

# --- LIST WITH ADVANCED FILTER ---
async def get_rooms(page: int, limit: int, filters: dict):
    skip = (page - 1) * limit
    query = {}

    if filters.get("name"):
        query["name"] = {"$regex": filters["name"], "$options": "i"}
    if filters.get("active") is not None:
        query["active"] = filters["active"]
    if filters.get("min_price") is not None:
        query.setdefault("price", {})["$gte"] = filters["min_price"]
    if filters.get("max_price") is not None:
        query.setdefault("price", {})["$lte"] = filters["max_price"]

    cursor = collection.find(query).skip(skip).limit(limit)
    rooms_list = await cursor.to_list(length=limit)
    total = await collection.count_documents(query)

    return {
        "data": rooms_schema(rooms_list), 
        "total": total,
        "page": page,
        "limit": limit,
    }

# --- UPDATE ---
async def update_room(room_id: str, data: dict, user_email: str):
    if not is_valid_object_id(room_id):
        return None

    data["updated_by"] = user_email
    data["updated_at"] = datetime.now(timezone.utc)

    await collection.update_one({"_id": ObjectId(room_id)}, {"$set": data})
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
    if not is_valid_object_id(room_id):
        return False

    result = await collection.delete_one({"_id": ObjectId(room_id)})
    return result.deleted_count > 0

# --- ADD IMAGES TO EXISTING ROOM ---
async def add_room_images_to_db(room_id: str, new_urls: list):
    if not is_valid_object_id(room_id):
        return False

    try:
        # 🟢 NUEVO: Verificamos si hay que establecer una main_image
        room = await collection.find_one({"_id": ObjectId(room_id)})
        
        update_query = {"$push": {"images": {"$each": new_urls}}}
        
        # Si la habitación no tenía imagen principal y estamos subiendo nuevas, asignamos la primera
        if room and not room.get("main_image") and new_urls:
            update_query["$set"] = {"main_image": new_urls[0]}

        result = await collection.update_one({"_id": ObjectId(room_id)}, update_query)
        return result.modified_count > 0
    except Exception as e:
        print(f"Error al actualizar array en MongoDB: {e}")
        return False

