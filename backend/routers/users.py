from fastapi import APIRouter, Depends, HTTPException, status
from backend.dependencies.auth import required_admin, get_current_user
from backend.models.user_models import user_entity
from backend.schemas.user_schema import UserUpdate
from backend.services.user_service import update_user_service, delete_user_service, deactivate_user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


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

    # Corregido: deactivate_user_service ahora está importado
    success = await deactivate_user_service(user_id)

    if not success:
        raise HTTPException(status_code=400, detail="No se pudo desactivar la cuenta")

    return {"message": "Cuenta desactivada correctamente. ¡Esperamos verte pronto!"}