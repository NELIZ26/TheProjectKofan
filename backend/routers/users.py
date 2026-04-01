from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from backend.db.client import db
from backend.dependencies.auth import required_admin, get_current_user
from backend.models.user_models import user_entity
from backend.schemas.user_schema import UserUpdate, UserCreate, AdminUserUpdate
from backend.services.user_service import (
    update_user_service, 
    delete_user_service, 
    deactivate_user_service,
    create_user_service,
    get_user_by_email,
    get_user_by_document
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# ==========================================
# 👤 RUTAS DE AUTOSERVICIO (Para el cliente en la web)
# ==========================================

@router.get("/me")
async def read_me(user=Depends(get_current_user)):
    return user_entity(user)

@router.patch("/update-me")
async def update_me(data: UserUpdate, current_user=Depends(get_current_user)):
    update_dict = data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(status_code=400, detail="No enviaste datos para actualizar")

    user_id = str(current_user["_id"])
    user_updated = await update_user_service(user_id, update_dict)

    if not user_updated:
        raise HTTPException(status_code=404, detail="No se pudo actualizar el usuario")

    user_updated["_id"] = str(user_updated["_id"])
    user_updated.pop("password", None)

    return {"message": "¡Perfil actualizado con éxito!", "user": user_updated}

@router.patch("/delete-me")
async def delete_me(current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    success = await deactivate_user_service(user_id)

    if not success:
        raise HTTPException(status_code=400, detail="No se pudo desactivar la cuenta")

    return {"message": "Cuenta desactivada correctamente. ¡Esperamos verte pronto!"}


# ==========================================
# 🛡️ RUTAS DE ADMINISTRADOR (Para el Dashboard Kofán)
# ==========================================

# 1. Obtener todos los usuarios (Clientes y Empleados)
@router.get("/", dependencies=[Depends(required_admin)])
async def get_all_users():
    users_cursor = db.clients.find()
    users = await users_cursor.to_list(length=1000)
    return [user_entity(user) for user in users]

# 2. Crear un usuario desde Recepción (Puede ser cliente o empleado)
@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(required_admin)])
async def create_user_by_admin(new_user: UserCreate):
    # Verificar si el correo ya existe
    if await get_user_by_email(new_user.email):
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    
    # Verificar si el documento ya existe
    if await get_user_by_document(new_user.number_document):
        raise HTTPException(status_code=400, detail="El número de documento ya está registrado.")

    # 🟢 TRUCO DE RECEPCIÓN: Si creas un cliente presencial y no le pones clave, 
    # le asignamos su número de cédula como contraseña temporal por defecto.
    if not new_user.password:
        new_user.password = new_user.number_document

    # Aquí SÍ se respeta el "role" que tú le mandes desde el panel (admin, recepcionista, client)
    new_id = await create_user_service(new_user)
    
    return {
        "message": "Usuario registrado exitosamente desde el panel",
        "user_id": new_id
    }

# 3. Editar cualquier usuario (Cambiar roles, actualizar datos)
@router.patch("/{user_id}", dependencies=[Depends(required_admin)])
async def update_user_by_admin(user_id: str, data: AdminUserUpdate):
    update_dict = data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    user_updated = await update_user_service(user_id, update_dict)

    if not user_updated:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_updated["_id"] = str(user_updated["_id"])
    user_updated.pop("password", None)

    return {"message": "Usuario actualizado por el administrador", "user": user_updated}

# 4. Eliminar un usuario (Desactivar cuenta)

@router.patch("/{user_id}/toggle-status")
async def toggle_user_status(user_id: str, current_user=Depends(get_current_user)):
    # 🟢 CORREGIDO: Buscamos y actualizamos en db.clients
    user = db.clients.find_one({"_id": ObjectId(user_id)}) 
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    current_status = user.get("is_active", True)
    new_status = not current_status

    db.clients.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": new_status}}
    )

    estado_str = "Reactivado" if new_status else "Suspendido"
    return {"message": f"Usuario {estado_str} correctamente", "is_active": new_status}