from typing import Optional

from fastapi import APIRouter, Depends
from backend.dependencies.auth import get_current_user, required_admin
from backend.schemas.booking_schema import ReservaCreate, EstadoReserva, UpdateEstadoReserva, ReservaPublicCreate, UpdateReservaDetalles
from backend.services.booking_service import create_booking_service, get_all_bookings_service, get_user_bookings_service, update_booking_status_service, update_booking_details_service
from fastapi import HTTPException, status
from enum import Enum
router = APIRouter(
    prefix="/api/reservas", 
    tags=["api/reservas"]
)

# PARA CREAR UNA RESERVA, SOLO USUARIOS AUTENTICADOS
@router.post("/")
async def registrar_reserva(reserva: ReservaCreate, user = Depends(get_current_user)):
    # Extraemos el ID del usuario directamente del token (el objeto 'user' que devuelve MongoDB)
    user_id_from_token = str(user["_id"])
    
    nueva_reserva_id = await create_booking_service(reserva, user_id_from_token)
    
    return {
        "message": "Reserva creada exitosamente",
        "reserva_id": nueva_reserva_id,
        "usuario_que_reservo": user["email"] # Opcional: para confirmar en la respuesta
    }

@router.post("/invitado")
async def registrar_reserva_publica(reserva: ReservaPublicCreate):
   
    nueva_reserva_id = await create_booking_service(reserva, user_id=None)
    
    return {
        "message": "¡Reserva recibida con éxito! Pronto nos comunicaremos contigo para confirmar el pago.",
        "reserva_id": nueva_reserva_id,
        "cliente": reserva.cliente_nombre
    }


# SOLO ADMIN PUEDE CAMBIAR EL ESTADO DE UNA RESERVA
@router.patch("/{reserva_id}/estado")
async def cambiar_estado_reserva(
    reserva_id: str, 
    datos_actualizacion: UpdateEstadoReserva, 
    admin_user = Depends(required_admin) 
):
    exito = await update_booking_status_service(
        reserva_id, 
        datos_actualizacion.estado.value, 
        datos_actualizacion.motivo_actualizacion,
        admin_user["email"]
    )
    
    if not exito:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
        
    return {
        "message": "Estado de la reserva actualizado exitosamente",
        "admin_que_autorizo": admin_user["email"],
        "nuevo_estado": datos_actualizacion.estado.value,
        "motivo": datos_actualizacion.motivo_actualizacion
    }


@router.get("/me")
async def listar_mis_reservas(user = Depends(get_current_user)):
    # 1. Extraemos el ID del usuario del token
    user_id = str(user["_id"])
    
    # 2. Llamamos al servicio para buscar sus reservas
    reservas = await get_user_bookings_service(user_id)
    
    return {
        "usuario": user["email"],
        "total_reservas": len(reservas),
        "reservas": reservas
    }



# 2. En el Router, usamos ese Enum
@router.get("/admin/todas")
async def get_all_bookings(
    # Ahora FastAPI solo aceptará uno de los 4 estados de arriba
    estado: Optional[EstadoReserva] = None, 
    admin_user = Depends(required_admin)
):
    return await get_all_bookings_service(estado_filtro=estado)

# 🟢 Asegúrate de importar esto arriba del todo:
# from backend.schemas.booking_schema import UpdateReservaDetalles
# from backend.services.booking_service import update_booking_details_service

# 🟢 LA NUEVA RUTA PARA COMPLETAR DATOS EN EL CHECK-IN
# 🟢 LA NUEVA RUTA PARA COMPLETAR DATOS EN EL CHECK-IN
@router.put("/{reserva_id}/detalles")
async def actualizar_detalles_reserva(
    reserva_id: str, 
    detalles: UpdateReservaDetalles, 
    admin_user = Depends(required_admin) 
):
    # Convertimos el modelo a diccionario
    datos_actualizados = detalles.model_dump()
    
    # 🟢 EL FIX: Convertimos los objetos 'date' a texto para que MongoDB sea feliz
    datos_actualizados["fecha_entrada"] = str(datos_actualizados["fecha_entrada"])
    datos_actualizados["fecha_salida"] = str(datos_actualizados["fecha_salida"])
    
    exito = await update_booking_details_service(reserva_id, datos_actualizados)
    
    if not exito:
        raise HTTPException(status_code=404, detail="Reserva no encontrada o no hubo cambios")
        
    return {
        "message": "Detalles de la reserva y acompañantes actualizados exitosamente",
        "admin": admin_user["email"]
    }