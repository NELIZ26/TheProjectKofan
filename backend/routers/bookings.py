from typing import Optional
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from backend.dependencies.auth import get_current_user, required_admin
from backend.schemas.booking_schema import ReservaCreate, EstadoReserva, UpdateEstadoReserva, ReservaPublicCreate, UpdateReservaDetalles
from backend.services.booking_service import create_booking_service, get_all_bookings_service, get_user_bookings_service, update_booking_status_service, update_booking_details_service
from enum import Enum
from backend.services.media_service import save_image
from datetime import datetime, timezone

router = APIRouter(
    prefix="/api/reservas", 
    tags=["api/reservas"]
)

# PARA CREAR UNA RESERVA, SOLO USUARIOS AUTENTICADOS
@router.post("/")
async def registrar_reserva(
    habitacion_id: str = Form(...),
    fecha_entrada: str = Form(...),
    fecha_salida: str = Form(...),
    monto_total: float = Form(...),
    cliente_nombre: str = Form(...),
    cliente_email: str = Form(...),
    cliente_celular: str = Form(...),
    observaciones: str = Form(None),
    comprobante: Optional[UploadFile] = File(None),
    user = Depends(get_current_user) # 🔒 Requiere Token
):
    # 1. Manejo del Comprobante
    ruta_comprobante = None
    if comprobante:
        ruta_comprobante = save_image(comprobante)

    # 2. Armamos el esquema manual (ReservaCreate)
    reserva_datos = ReservaCreate(
        habitacion_id=habitacion_id,
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        monto_total=monto_total,
        cliente_nombre=cliente_nombre,
        cliente_email=cliente_email,
        cliente_celular=cliente_celular,
        tipo_persona="natural",
        tipo_documento="CC", 
        cliente_documento="0",
        observaciones=observaciones,
        comprobante_url=ruta_comprobante
    )

    # 3. Extraemos el ID del usuario directamente del token
    user_id_from_token = str(user["_id"])
    
    # 4. Guardamos la reserva vinculándola al ID del usuario
    nueva_reserva_id = await create_booking_service(reserva_datos, user_id_from_token)
    
    return {
        "message": "Reserva creada exitosamente",
        "reserva_id": nueva_reserva_id,
        "usuario_que_reservo": user["email"] 
    }

@router.post("/invitado")
async def registrar_reserva_publica(
    habitacion_id: str = Form(...),
    fecha_entrada: str = Form(...),
    fecha_salida: str = Form(...),
    monto_total: float = Form(...),
    cliente_nombre: str = Form(...),
    cliente_email: str = Form(...),
    cliente_celular: str = Form(...),
    observaciones: str = Form(None),
    comprobante: Optional[UploadFile] = File(None) 
):
    ruta_comprobante = None
    if comprobante:
        ruta_comprobante = save_image(comprobante)

    # 2. Armamos el esquema manual que antes FastAPI hacía automático
    reserva_datos = ReservaPublicCreate(
        habitacion_id=habitacion_id,
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        monto_total=monto_total,
        cliente_nombre=cliente_nombre,
        cliente_email=cliente_email,
        cliente_celular=cliente_celular,
        tipo_persona="natural",
        tipo_documento="CC",
        cliente_documento="0",
        observaciones=observaciones,
        comprobante_url=ruta_comprobante
    )
   
    # 3. Guardamos la reserva en MongoDB
    nueva_reserva_id = await create_booking_service(reserva_datos, user_id=None)
    
    return {
        "message": "¡Reserva y comprobante recibidos con éxito!",
        "reserva_id": nueva_reserva_id,
        "cliente": cliente_nombre
    }


# 🟢 SOLO ADMIN PUEDE CAMBIAR EL ESTADO DE UNA RESERVA (AQUÍ ESTÁ LA CORRECCIÓN)
@router.patch("/{reserva_id}/estado")
async def cambiar_estado_reserva(
    reserva_id: str, 
    datos_actualizacion: UpdateEstadoReserva, 
    admin_user = Depends(required_admin) 
):
    exito = await update_booking_status_service(
        reserva_id=reserva_id, 
        nuevo_estado=datos_actualizacion.estado.value, 
        motivo=datos_actualizacion.motivo_actualizacion,
        admin_email=admin_user["email"],
        admin_id=str(admin_user["_id"]) # 🟢 LE PASAMOS EL ID AL SERVICIO PARA QUE CREE LA NOTIFICACIÓN
    )
    
    if not exito:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
        
    return {
        "message": "Estado de la reserva actualizado exitosamente",
        "admin_que_autorizo": admin_user["email"],
        "nuevo_estado": datos_actualizacion.estado.value,
        "motivo": datos_actualizacion.motivo_actualizacion
    }


@router.get("/mis-reservas")
async def listar_mis_reservas(user = Depends(get_current_user)):
    try:
        # 1. Extraemos el ID del usuario de forma segura
        user_id = str(user["_id"])
        
        # 2. Vamos a la base de datos a buscar sus reservas
        reservas = await get_user_bookings_service(user_id)
        
        # 3. Validamos que SIEMPRE devuelva una lista (incluso si está vacía)
        if not reservas:
            return []
            
        return reservas

    except Exception as e:
        # 4. Si algo explota en la BD, se lo decimos educadamente al frontend
        print(f"Error interno al buscar reservas: {e}") 
        raise HTTPException(
            status_code=500, 
            detail="Tuvimos un problema interno al cargar tus reservas. Intenta de nuevo."
        )


@router.get("/admin/todas")
async def get_all_bookings(
    estados: Optional[str] = None, 
    page: int = 1,     
    limit: int = 10,   
    admin_user = Depends(required_admin)
):
    return await get_all_bookings_service(estados_filtro=estados, page=page, limit=limit)


@router.put("/{reserva_id}/detalles")
async def actualizar_detalles_reserva(
    reserva_id: str, 
    detalles: UpdateReservaDetalles, 
    admin_user = Depends(required_admin) 
):
    # Convertimos el modelo a diccionario
    datos_actualizados = detalles.model_dump()
    
    # Convertimos los strings del frontend a datetime UTC para MongoDB
    try:
        entrada_dt = datetime.strptime(datos_actualizados["fecha_entrada"], "%Y-%m-%d")
        salida_dt = datetime.strptime(datos_actualizados["fecha_salida"], "%Y-%m-%d")
        
        # Inyectamos los objetos datetime con zona horaria UTC de vuelta al diccionario
        datos_actualizados["fecha_entrada"] = entrada_dt.replace(tzinfo=timezone.utc)
        datos_actualizados["fecha_salida"] = salida_dt.replace(tzinfo=timezone.utc)
        
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="Formato de fecha inválido. Por favor usa el formato YYYY-MM-DD."
        )
    
    # Enviamos los datos limpios y en el formato correcto a MongoDB
    exito = await update_booking_details_service(reserva_id, datos_actualizados)
    
    if not exito:
        raise HTTPException(status_code=404, detail="Reserva no encontrada o no hubo cambios")
        
    return {
        "message": "Detalles de la reserva y acompañantes actualizados exitosamente",
        "admin": admin_user["email"]
    }