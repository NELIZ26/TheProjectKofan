from fastapi import APIRouter, Depends
from typing import List 
from backend.dependencies.auth import get_current_user
from backend.services.notifications_service import get_notificaciones_usuario, marcar_todas_leidas_service
from backend.schemas.notification_schema import NotificationResponse # 🟢 Importamos el esquema

router = APIRouter(prefix="/api/notificaciones", tags=["Notificaciones"])

# 🟢 Le decimos a FastAPI que esta ruta devuelve una Lista de NotificationResponse
@router.get("/mis-avisos", response_model=List[NotificationResponse])
async def obtener_mis_avisos(user = Depends(get_current_user)):
    user_id = str(user["_id"])
    avisos = await get_notificaciones_usuario(user_id)
    return avisos

@router.patch("/read-all")
async def marcar_leidas(user = Depends(get_current_user)):
    user_id = str(user["_id"])
    actualizadas = await marcar_todas_leidas_service(user_id)
    return {"message": "Avisos marcados como leídos", "modificadas": actualizadas}