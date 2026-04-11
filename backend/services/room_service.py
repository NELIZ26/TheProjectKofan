import shutil
import uuid
from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from backend.db.client import db 
from backend.schemas.room_schema import room_schema, rooms_schema

collection = db.rooms
logs_collection = db.room_logs 

# --- HELPER: Validar ObjectId ---
def is_valid_object_id(id_str: str) -> bool:
    try:
        ObjectId(id_str)
        return True
    except InvalidId:
        return False

# --- HELPER: Registrar movimientos ---
async def log_room_movement(room_id: str, room_name: str, action: str, user_email: str, changes: list = None):
    log_entry = {
        "room_id": str(room_id),
        "room_name": room_name,
        "action": action,
        "user": user_email,
        "changes": changes or [], 
        "timestamp": datetime.now(timezone.utc)
    }
    await logs_collection.insert_one(log_entry)

# --- GET LOGS: Obtener historial para el Dashboard ---
async def get_room_logs(page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    
    # Ordenamos por fecha descendente (más nuevos primero)
    cursor = logs_collection.find().sort("timestamp", -1).skip(skip).limit(limit)
    logs = await cursor.to_list(length=limit)
    
    # Contamos el total para saber cuántas páginas hay
    total = await logs_collection.count_documents({})
    
    for log in logs:
        log["_id"] = str(log["_id"])
        
    return {
        "data": logs,
        "total": total,
        "page": page,
        "limit": limit
    }

# --- CREATE ---
async def create_room(data: dict, user_email: str):
    now = datetime.now(timezone.utc)

    data["created_by"] = user_email
    data["updated_by"] = user_email
    data["created_at"] = now
    data["updated_at"] = now
    
    if "is_available" not in data:
        data["is_available"] = True

    if "active" not in data:
        data["active"] = True

    result = await collection.insert_one(data)
    new_room = await collection.find_one({"_id": result.inserted_id})
    
    # Registramos la creación
    await log_room_movement(result.inserted_id, data.get("name", "Sin nombre"), "CREACIÓN", user_email)
    
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

    old_room = await collection.find_one({"_id": ObjectId(room_id)})
    if not old_room:
        return None

    changes = []
    for key, new_value in data.items():
        # Ignoramos campos que no importa rastrear
        if key in ["updated_at", "updated_by", "_id", "id", "created_at", "images", "main_image"]:
            continue
            
        old_value = old_room.get(key)
        
        # Comparamos listas (ej: amenities)
        if isinstance(old_value, list) and isinstance(new_value, list):
            if sorted(old_value) != sorted(new_value):
                changes.append({"field": key, "old": old_value, "new": new_value})
        
        # Comparamos valores normales
        elif old_value != new_value:
            changes.append({
                "field": key,
                "old": old_value,
                "new": new_value
            })

    # Actualizamos la DB
    data["updated_by"] = user_email
    data["updated_at"] = datetime.now(timezone.utc)
    await collection.update_one({"_id": ObjectId(room_id)}, {"$set": data})
    
    # Registramos el log
    if changes:
        await log_room_movement(room_id, old_room.get("name"), "ACTUALIZACIÓN", user_email, changes)
    else:
        await log_room_movement(room_id, old_room.get("name"), "ACTUALIZACIÓN", user_email, [])
    
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
    if room.get("main_image") == url:
        update_data["main_image"] = images[0] if images else None

    # Se llama a update_room, el cual ya tiene su propio registro de ACTUALIZACIÓN
    return await update_room(room_id, update_data, user_email)

# --- DELETE ---
async def delete_room(room_id: str, user_email: str):
    if not is_valid_object_id(room_id):
        return False

    room_before = await collection.find_one({"_id": ObjectId(room_id)})
    if not room_before:
        return False

    result = await collection.delete_one({"_id": ObjectId(room_id)})
    
    # Registramos la eliminación
    if result.deleted_count > 0:
        await log_room_movement(room_id, room_before.get("name", "Sin nombre"), "ELIMINACIÓN", user_email)
        return True
    return False

# --- ADD IMAGES TO EXISTING ROOM ---
async def add_room_images_to_db(room_id: str, new_urls: list, user_email: str):
    if not is_valid_object_id(room_id):
        return False

    try:
        room = await collection.find_one({"_id": ObjectId(room_id)})
        update_query = {"$push": {"images": {"$each": new_urls}}}
        
        if room and not room.get("main_image") and new_urls:
            update_query["$set"] = {"main_image": new_urls[0]}

        result = await collection.update_one({"_id": ObjectId(room_id)}, update_query)
        
        # Registramos que se agregaron fotos
        if result.modified_count > 0:
            await log_room_movement(room_id, room.get("name", "Sin nombre"), "ACTUALIZACIÓN (Fotos)", user_email)
            return True
            
        return False
    except Exception as e:
        pass
        return False

