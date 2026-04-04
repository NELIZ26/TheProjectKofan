from backend.db.client import db
from backend.core.security import hash_password
from bson import ObjectId
from pymongo import ReturnDocument

async def create_user_service(user_data):
    if not isinstance(user_data, dict):
        user_data = user_data.model_dump()
    raw_password = user_data.get("password") or user_data.get("number_document")
    
    if not raw_password:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Se requiere contraseña o número de documento")
    user_data["password"] = hash_password(raw_password)
    result = await db.clients.insert_one(user_data)
    return str(result.inserted_id)

async def update_user_service(user_id: str, update_data: dict):
    # Operación atómica: Actualiza y devuelve el nuevo documento en un solo paso
    return await db.clients.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

async def delete_user_service(user_id: str):
    result = await db.clients.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

async def get_user_by_email(email: str):
    return await db.clients.find_one({"email": email})

async def get_user_by_document(doc: str):
    return await db.clients.find_one({"number_document": doc})

async def get_user_by_id(user_id: str):
    return await db.clients.find_one({"_id": ObjectId(user_id)})

async def deactivate_user_service(user_id: str):
    result = await db.clients.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False}}
    )
    return result.matched_count > 0

async def toggle_user_status_service(user_id: str):
    user = await db.clients.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None
    
    new_status = not user.get("is_active", True)
    await db.clients.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": new_status}}
    )
    return new_status

# 🟢 CORRECCIÓN: Función fusionada (Paginación + Limpieza de datos)
async def get_all_users_service(skip: int = 0, limit: int = 50):
    cursor = db.clients.find().skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    
    for user in users:
        user["_id"] = str(user["_id"])
        user.pop("password", None) # Por seguridad, nunca devolvemos el hash
        
    return users