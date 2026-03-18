from backend.db.client import db
from backend.core.security import hash_password
from bson import ObjectId


async def create_user_service(user_data):
    user_dict = user_data.model_dump()
    user_dict["password"] = hash_password(user_data.password)
    result = await db.clients.insert_one(user_dict)
    return str(result.inserted_id)


async def update_user_service(user_id: str, update_data: dict):
    await db.clients.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return await db.clients.find_one({"_id": ObjectId(user_id)})


async def delete_user_service(user_id: str):
    result = await db.clients.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0


async def get_user_by_email(email: str):
    return await db.clients.find_one({"email": email})


async def get_user_by_document(doc: str):
    # Corregido: el campo en UserCreate es "number_document", no "document_number"
    return await db.clients.find_one({"number_document": doc})


async def get_user_by_id(user_id: str):
    return await db.clients.find_one({"_id": ObjectId(user_id)})


async def get_all_users_service():
    users_cursor = db.clients.find()
    users = await users_cursor.to_list(length=100)
    for user in users:
        user["_id"] = str(user["_id"])
        user.pop("password", None)
    return users


async def deactivate_user_service(user_id: str):
    result = await db.clients.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False}}
    )
    return result.matched_count > 0